#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║  PROFESSEUR AGENT v5 — FICHIER UNIQUE COMPLET                 ║
║  Programme 200 jours · PDF A4 · 19h00 Maroc                   ║
║  Anglais · Espagnol · Arabe (calligraphie) · Maths · Logique  ║
╚═══════════════════════════════════════════════════════════════╝
"""
import io, os, re, sys, json, time, random, smtplib, logging
from datetime import date, datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base     import MIMEBase
from email.mime.text     import MIMEText
from email               import encoders
try:
    import pytz, requests as _req
    from groq  import Groq
    from PIL   import Image as PI, ImageDraw, ImageFont
    from reportlab.lib.pagesizes import A4
    from reportlab.lib            import colors
    from reportlab.lib.units      import cm
    from reportlab.lib.styles     import ParagraphStyle
    from reportlab.lib.enums      import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.platypus       import (Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, BaseDocTemplate, PageTemplate, Frame, NextPageTemplate)
    from reportlab.pdfbase        import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_AR = True
except ImportError as _e:
    print(f"[ERR] {_e} → pip install -r requirements.txt"); HAS_AR = False

# ═══════════════════ CONFIG ══════════════════════════════════════
GROQ_KEY    = os.environ.get("GROQ_API_KEY","")
GMAIL_USER  = os.environ.get("GMAIL_USER","")
GMAIL_PASS  = os.environ.get("GMAIL_APP_PASSWORD","")
EMAIL_TO    = os.environ.get("PROFESSOR_EMAIL_TO","")
RESEND_KEY  = os.environ.get("RESEND_API_KEY","")
EMAIL_FROM  = os.environ.get("PROFESSOR_EMAIL_FROM","professeur@baraka-bvc.com")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY","")
PEXELS_KEY  = os.environ.get("PEXELS_API_KEY","")
START_DATE  = date.fromisoformat(os.environ.get("PROFESSOR_START_DATE","2026-06-09"))
try:    MOROCCO = pytz.timezone("Africa/Casablanca")
except: MOROCCO = None
IMG_CACHE   = Path("/tmp/prof_cache"); IMG_CACHE.mkdir(exist_ok=True)
W, H = A4;  CW = W - 3*cm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PROF] %(message)s")
log = logging.getLogger()

_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_EMOJ = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
_ARR  = "/usr/share/fonts/truetype/kacst/KacstBook.ttf"
_ARB  = "/usr/share/fonts/truetype/kacst-one/KacstOne-Bold.ttf"

for _n,_p in [("KacstR",_ARR),("KacstB",_ARB)]:
    if Path(_p).exists():
        try: pdfmetrics.registerFont(TTFont(_n,_p))
        except: pass

def hx(h): return colors.HexColor(h)
def ps(n,**k): return ParagraphStyle(n,**k)
def _fnt(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()
def _ar(t):
    if not t or not HAS_AR: return t
    try: return get_display(arabic_reshaper.reshape(t))
    except: return t

# ═══════════════════ WORD BANK (377 mots) ═══════════════════════
_W=[("apple","manzana","تفاحة","pomme","apple","fruits"),("banana","plátano","موزة","banane","banana","fruits"),("orange","naranja","برتقالة","orange","orange fruit","fruits"),("strawberry","fresa","فراولة","fraise","strawberry","fruits"),("grape","uva","عنب","raisin","grapes","fruits"),("mango","mango","مانجو","mangue","mango","fruits"),("watermelon","sandía","بطيخ","pastèque","watermelon","fruits"),("pineapple","piña","أناناس","ananas","pineapple","fruits"),("cherry","cereza","كرز","cerise","cherries","fruits"),("peach","melocotón","خوخ","pêche","peach","fruits"),("pear","pera","كمثرى","poire","pear","fruits"),("lemon","limón","ليمون","citron","lemon","fruits"),("coconut","coco","جوز الهند","noix de coco","coconut","fruits"),("kiwi","kiwi","كيوي","kiwi","kiwi","fruits"),("avocado","aguacate","أفوكادو","avocat","avocado","fruits"),("blueberry","arándano","توت أزرق","myrtille","blueberries","fruits"),("pomegranate","granada","رمان","grenade","pomegranate","fruits"),("melon","melón","شمام","melon","melon","fruits"),("tangerine","mandarina","يوسفي","mandarine","mandarine","fruits"),("papaya","papaya","بابايا","papaye","papaya","fruits"),("lime","lima","ليمون أخضر","citron vert","lime","fruits"),("fig","higo","تين","figue","fig","fruits"),("date","dátil","تمر","datte","dates fruit","fruits"),("guava","guayaba","جوافة","goyave","guava","fruits"),("passion fruit","maracuyá","فاكهة الباشن","fruit passion","passion fruit","fruits"),("carrot","zanahoria","جزرة","carotte","carrot","vegetables"),("tomato","tomate","طماطم","tomate","tomato","vegetables"),("potato","patata","بطاطا","pomme de terre","potato","vegetables"),("onion","cebolla","بصلة","oignon","onion","vegetables"),("cucumber","pepino","خيار","concombre","cucumber","vegetables"),("pepper","pimiento","فلفل","poivron","pepper","vegetables"),("spinach","espinaca","سبانخ","épinard","spinach","vegetables"),("broccoli","brócoli","بروكلي","brocoli","broccoli","vegetables"),("corn","maíz","ذرة","maïs","corn","vegetables"),("peas","guisantes","بازلاء","petits pois","peas","vegetables"),("lettuce","lechuga","خس","laitue","lettuce","vegetables"),("mushroom","champiñón","فطر","champignon","mushroom","vegetables"),("eggplant","berenjena","باذنجان","aubergine","eggplant","vegetables"),("zucchini","calabacín","كوسة","courgette","zucchini","vegetables"),("garlic","ajo","ثوم","ail","garlic","vegetables"),("pumpkin","calabaza","قرع","citrouille","pumpkin","vegetables"),("cabbage","col","كرنب","chou","cabbage","vegetables"),("sweet potato","boniato","بطاطا حلوة","patate douce","sweet potato","vegetables"),("cauliflower","coliflor","قرنبيط","chou-fleur","cauliflower","vegetables"),("asparagus","espárrago","هليون","asperge","asparagus","vegetables"),("beetroot","remolacha","شمندر","betterave","beetroot","vegetables"),("cat","gato","قطة","chat","cat","animals"),("dog","perro","كلب","chien","dog","animals"),("rabbit","conejo","أرنب","lapin","rabbit","animals"),("hamster","hámster","هامستر","hamster","hamster","animals"),("parrot","loro","ببغاء","perroquet","parrot","animals"),("goldfish","pez dorado","سمكة ذهبية","poisson rouge","goldfish","animals"),("turtle","tortuga","سلحفاة","tortue","turtle","animals"),("horse","caballo","حصان","cheval","horse","animals"),("cow","vaca","بقرة","vache","cow","animals"),("sheep","oveja","خروف","mouton","sheep","animals"),("goat","cabra","ماعز","chèvre","goat","animals"),("chicken","gallina","دجاجة","poule","chicken","animals"),("duck","pato","بطة","canard","duck","animals"),("donkey","burro","حمار","âne","donkey","animals"),("mouse","ratón","فأر","souris","mouse","animals"),("guinea pig","cobaya","خنزير غيني","cobaye","guinea pig","animals"),("canary","canario","كناري","canari","canary","animals"),("rooster","gallo","ديك","coq","rooster","animals"),("lion","león","أسد","lion","lion","wild_animals"),("tiger","tigre","نمر","tigre","tiger","wild_animals"),("elephant","elefante","فيل","éléphant","elephant","wild_animals"),("giraffe","jirafa","زرافة","girafe","giraffe","wild_animals"),("zebra","cebra","حمار وحشي","zèbre","zebra","wild_animals"),("monkey","mono","قرد","singe","monkey","wild_animals"),("gorilla","gorila","غوريلا","gorille","gorilla","wild_animals"),("bear","oso","دب","ours","bear","wild_animals"),("wolf","lobo","ذئب","loup","wolf","wild_animals"),("fox","zorro","ثعلب","renard","fox","wild_animals"),("deer","ciervo","غزال","cerf","deer","wild_animals"),("crocodile","cocodrilo","تمساح","crocodile","crocodile","wild_animals"),("hippopotamus","hipopótamo","فرس البحر","hippopotame","hippo","wild_animals"),("rhinoceros","rinoceronte","وحيد القرن","rhinocéros","rhinoceros","wild_animals"),("cheetah","guepardo","فهد","guépard","cheetah","wild_animals"),("kangaroo","canguro","كنغر","kangourou","kangaroo","wild_animals"),("koala","koala","كوالا","koala","koala","wild_animals"),("panda","panda","باندا","panda","panda","wild_animals"),("polar bear","oso polar","دب قطبي","ours polaire","polar bear","wild_animals"),("camel","camello","جمل","chameau","camel","wild_animals"),("snake","serpiente","ثعبان","serpent","snake","wild_animals"),("frog","rana","ضفدع","grenouille","frog","wild_animals"),("squirrel","ardilla","سنجاب","écureuil","squirrel","wild_animals"),("hedgehog","erizo","قنفذ","hérisson","hedgehog","wild_animals"),("penguin","pingüino","بطريق","pingouin","penguin","wild_animals"),("dolphin","delfín","دلفين","dauphin","dolphin","sea"),("whale","ballena","حوت","baleine","whale","sea"),("shark","tiburón","قرش","requin","shark","sea"),("octopus","pulpo","أخطبوط","pieuvre","octopus","sea"),("crab","cangrejo","سرطان البحر","crabe","crab","sea"),("seahorse","caballito de mar","أبو رمال","hippocampe","seahorse","sea"),("starfish","estrella de mar","نجم البحر","étoile de mer","starfish","sea"),("jellyfish","medusa","قنديل البحر","méduse","jellyfish","sea"),("lobster","langosta","كركند","homard","lobster","sea"),("clownfish","pez payaso","سمكة مهرج","poisson clown","clownfish","sea"),("seal","foca","فقمة","phoque","seal","sea"),("eagle","águila","نسر","aigle","eagle","birds"),("owl","búho","بوم","hibou","owl","birds"),("flamingo","flamenco","نحام","flamant rose","flamingo","birds"),("peacock","pavo real","طاووس","paon","peacock","birds"),("toucan","tucán","طوقان","toucan","toucan","birds"),("hummingbird","colibrí","طائر طنان","colibri","hummingbird","birds"),("sparrow","gorrión","عصفور","moineau","sparrow","birds"),("swan","cisne","بجعة","cygne","swan","birds"),("butterfly","mariposa","فراشة","papillon","butterfly","insects"),("bee","abeja","نحلة","abeille","bee","insects"),("ladybug","mariquita","دعسوقة","coccinelle","ladybug","insects"),("ant","hormiga","نملة","fourmi","ant","insects"),("bread","pan","خبز","pain","bread","food"),("rice","arroz","أرز","riz","rice","food"),("pasta","pasta","مكرونة","pâtes","pasta","food"),("pizza","pizza","بيتزا","pizza","pizza","food"),("soup","sopa","شوربة","soupe","soup","food"),("egg","huevo","بيضة","œuf","egg","food"),("cheese","queso","جبن","fromage","cheese","food"),("butter","mantequilla","زبدة","beurre","butter","food"),("honey","miel","عسل","miel","honey","food"),("sandwich","sándwich","ساندويتش","sandwich","sandwich","food"),("hamburger","hamburguesa","همبرغر","hamburger","hamburger","food"),("cake","pastel","كعكة","gâteau","cake","food"),("cookie","galleta","كوكيز","biscuit","cookie","food"),("ice cream","helado","آيس كريم","glace","ice cream","food"),("chocolate","chocolate","شوكولاتة","chocolat","chocolate","food"),("chips","patatas fritas","رقائق","chips","chips","food"),("popcorn","palomitas","فشار","popcorn","popcorn","food"),("candy","caramelo","حلوى","bonbon","candy","food"),("jam","mermelada","مربى","confiture","jam","food"),("yogurt","yogur","زبادي","yaourt","yogurt","food"),("pancake","tortita","فطيرة","crêpe","pancake","food"),("croissant","croissant","كرواسان","croissant","croissant","food"),("donut","donut","دونات","donut","donut","food"),("salad","ensalada","سلطة","salade","salad","food"),("meat","carne","لحم","viande","meat","food"),("waffle","gofre","وافل","gaufre","waffle","food"),("water","agua","ماء","eau","water","drinks"),("milk","leche","حليب","lait","milk","drinks"),("juice","zumo","عصير","jus","juice","drinks"),("tea","té","شاي","thé","tea","drinks"),("coffee","café","قهوة","café","coffee","drinks"),("lemonade","limonada","ليمونادة","limonade","lemonade","drinks"),("smoothie","batido","عصير سموذي","smoothie","smoothie","drinks"),("hot chocolate","chocolate caliente","شوكولاتة ساخنة","chocolat chaud","hot chocolate","drinks"),("mint tea","té de menta","شاي بالنعناع","thé à la menthe","mint tea","drinks"),("milkshake","batido de leche","ميلك شيك","milkshake","milkshake","drinks"),("head","cabeza","رأس","tête","head","body"),("hair","pelo","شعر","cheveux","hair","body"),("eye","ojo","عين","œil","eye","body"),("ear","oreja","أذن","oreille","ear","body"),("nose","nariz","أنف","nez","nose","body"),("mouth","boca","فم","bouche","mouth","body"),("tooth","diente","سن","dent","teeth","body"),("hand","mano","يد","main","hand","body"),("finger","dedo","إصبع","doigt","finger","body"),("arm","brazo","ذراع","bras","arm","body"),("leg","pierna","ساق","jambe","leg","body"),("foot","pie","قدم","pied","foot","body"),("shoulder","hombro","كتف","épaule","shoulder","body"),("knee","rodilla","ركبة","genou","knee","body"),("heart","corazón","قلب","cœur","heart","body"),("brain","cerebro","مخ","cerveau","brain","body"),("muscle","músculo","عضلة","muscle","muscle","body"),("red","rojo","أحمر","rouge","red","colors"),("blue","azul","أزرق","bleu","blue","colors"),("yellow","amarillo","أصفر","jaune","yellow","colors"),("green","verde","أخضر","vert","green","colors"),("orange","naranja","برتقالي","orange","orange color","colors"),("purple","morado","بنفسجي","violet","purple","colors"),("pink","rosa","وردي","rose","pink","colors"),("black","negro","أسود","noir","black","colors"),("white","blanco","أبيض","blanc","white","colors"),("brown","marrón","بني","marron","brown","colors"),("grey","gris","رمادي","gris","grey","colors"),("shirt","camisa","قميص","chemise","shirt","clothes"),("t-shirt","camiseta","تيشيرت","t-shirt","t-shirt","clothes"),("dress","vestido","فستان","robe","dress","clothes"),("pants","pantalón","بنطلون","pantalon","pants","clothes"),("jacket","chaqueta","جاكيت","veste","jacket","clothes"),("coat","abrigo","معطف","manteau","coat","clothes"),("sweater","suéter","بلوزة","pull","sweater","clothes"),("shoes","zapatos","أحذية","chaussures","shoes","clothes"),("boots","botas","حذاء بوت","bottes","boots","clothes"),("sneakers","zapatillas","حذاء رياضي","baskets","sneakers","clothes"),("sandals","sandalias","صندل","sandales","sandals","clothes"),("socks","calcetines","جوارب","chaussettes","socks","clothes"),("hat","sombrero","قبعة","chapeau","hat","clothes"),("cap","gorra","طاقية","casquette","cap","clothes"),("scarf","bufanda","وشاح","écharpe","scarf","clothes"),("gloves","guantes","قفازات","gants","gloves","clothes"),("pajamas","pijama","بيجاما","pyjama","pajamas","clothes"),("swimsuit","bañador","ملابس سباحة","maillot de bain","swimsuit","clothes"),("raincoat","impermeable","معطف مطر","imperméable","raincoat","clothes"),("house","casa","بيت","maison","house","home"),("door","puerta","باب","porte","door","home"),("window","ventana","نافذة","fenêtre","window","home"),("kitchen","cocina","مطبخ","cuisine","kitchen","home"),("bedroom","dormitorio","غرفة نوم","chambre","bedroom","home"),("bathroom","baño","حمام","salle de bain","bathroom","home"),("living room","sala de estar","غرفة معيشة","salon","living room","home"),("bed","cama","سرير","lit","bed","home"),("chair","silla","كرسي","chaise","chair","home"),("table","mesa","طاولة","table","table","home"),("sofa","sofá","أريكة","canapé","sofa","home"),("lamp","lámpara","مصباح","lampe","lamp","home"),("fridge","nevera","ثلاجة","réfrigérateur","fridge","home"),("oven","horno","فرن","four","oven","home"),("shower","ducha","دش","douche","shower","home"),("television","televisión","تلفاز","télévision","tv","home"),("garden","jardín","حديقة","jardin","garden","home"),("stairs","escaleras","سلم","escalier","stairs","home"),("school","escuela","مدرسة","école","school","school"),("classroom","aula","فصل دراسي","salle de classe","classroom","school"),("teacher","profesor","معلم","professeur","teacher","school"),("book","libro","كتاب","livre","book","school"),("notebook","cuaderno","دفتر","cahier","notebook","school"),("pencil","lápiz","قلم رصاص","crayon","pencil","school"),("pen","bolígrafo","قلم","stylo","pen","school"),("eraser","goma","ممحاة","gomme","eraser","school"),("ruler","regla","مسطرة","règle","ruler","school"),("scissors","tijeras","مقص","ciseaux","scissors","school"),("glue","pegamento","غراء","colle","glue","school"),("backpack","mochila","حقيبة مدرسية","cartable","backpack","school"),("board","pizarra","سبورة","tableau","blackboard","school"),("calculator","calculadora","آلة حاسبة","calculatrice","calculator","school"),("globe","globo terráqueo","كرة الأرض","globe terrestre","globe","school"),("map","mapa","خريطة","carte","map","school"),("car","coche","سيارة","voiture","car","transport"),("bus","autobús","حافلة","bus","bus","transport"),("train","tren","قطار","train","train","transport"),("airplane","avión","طائرة","avion","airplane","transport"),("boat","barco","قارب","bateau","boat","transport"),("bicycle","bicicleta","دراجة","vélo","bicycle","transport"),("motorcycle","moto","دراجة نارية","moto","motorcycle","transport"),("truck","camión","شاحنة","camion","truck","transport"),("ambulance","ambulancia","سيارة إسعاف","ambulance","ambulance","transport"),("helicopter","helicóptero","طائرة مروحية","hélicoptère","helicopter","transport"),("taxi","taxi","تاكسي","taxi","taxi","transport"),("scooter","patinete","سكوتر","trottinette","scooter","transport"),("rocket","cohete","صاروخ","fusée","rocket","transport"),("sun","sol","شمس","soleil","sun","nature"),("moon","luna","قمر","lune","moon","nature"),("star","estrella","نجمة","étoile","star","nature"),("cloud","nube","سحابة","nuage","cloud","nature"),("rain","lluvia","مطر","pluie","rain","nature"),("snow","nieve","ثلج","neige","snow","nature"),("rainbow","arcoíris","قوس قزح","arc-en-ciel","rainbow","nature"),("tree","árbol","شجرة","arbre","tree","nature"),("flower","flor","زهرة","fleur","flower","nature"),("river","río","نهر","rivière","river","nature"),("ocean","océano","محيط","océan","ocean","nature"),("mountain","montaña","جبل","montagne","mountain","nature"),("desert","desierto","صحراء","désert","desert","nature"),("forest","bosque","غابة","forêt","forest","nature"),("beach","playa","شاطئ","plage","beach","nature"),("lake","lago","بحيرة","lac","lake","nature"),("spring","primavera","ربيع","printemps","spring","nature"),("summer","verano","صيف","été","summer","nature"),("autumn","otoño","خريف","automne","autumn","nature"),("winter","invierno","شتاء","hiver","winter","nature"),("wind","viento","ريح","vent","wind","nature"),("volcano","volcán","بركان","volcan","volcano","nature"),("island","isla","جزيرة","île","island","nature"),("waterfall","cascada","شلال","cascade","waterfall","nature"),("mother","madre","أم","mère","mother","family"),("father","padre","أب","père","father","family"),("sister","hermana","أخت","sœur","sisters","family"),("brother","hermano","أخ","frère","brothers","family"),("grandmother","abuela","جدة","grand-mère","grandmother","family"),("grandfather","abuelo","جد","grand-père","grandfather","family"),("baby","bebé","رضيع","bébé","baby","family"),("girl","niña","بنت","fille","girl","family"),("boy","niño","ولد","garçon","boy","family"),("friend","amigo","صديق","ami","friends","family"),("doctor","médico","طبيب","médecin","doctor","family"),("nurse","enfermera","ممرضة","infirmière","nurse","family"),("police","policía","شرطي","policier","police","family"),("firefighter","bombero","إطفائي","pompier","firefighter","family"),("chef","cocinero","طاهٍ","chef cuisinier","chef","family"),("farmer","agricultor","مزارع","agriculteur","farmer","family"),("pilot","piloto","طيار","pilote","pilot","family"),("astronaut","astronauta","رائد فضاء","astronaute","astronaut","family"),("football","fútbol","كرة القدم","football","football","sports"),("basketball","baloncesto","كرة السلة","basketball","basketball","sports"),("tennis","tenis","تنس","tennis","tennis","sports"),("swimming","natación","سباحة","natation","swimming","sports"),("cycling","ciclismo","ركوب الدراجة","cyclisme","cycling","sports"),("running","correr","الجري","course","running","sports"),("gymnastics","gimnasia","جمباز","gymnastique","gymnastics","sports"),("skiing","esquí","تزلج","ski","skiing","sports"),("surfing","surf","ركوب الأمواج","surf","surfing","sports"),("boxing","boxeo","ملاكمة","boxe","boxing","sports"),("chess","ajedrez","شطرنج","échecs","chess","sports"),("puzzle","puzzle","أحجية","puzzle","puzzle","sports"),("kite","cometa","طائرة ورقية","cerf-volant","kite","sports"),("trampoline","trampolín","ترامبولين","trampoline","trampoline","sports"),("bowling","bolos","بولينغ","bowling","bowling","sports"),("ping pong","ping-pong","تنس طاولة","ping-pong","ping pong","sports"),("happy","feliz","سعيد","heureux","happy","emotions"),("sad","triste","حزين","triste","sad","emotions"),("angry","enfadado","غاضب","en colère","angry","emotions"),("scared","asustado","خائف","effrayé","scared","emotions"),("surprised","sorprendido","مندهش","surpris","surprised","emotions"),("excited","emocionado","متحمس","excité","excited","emotions"),("tired","cansado","متعب","fatigué","tired","emotions"),("hungry","hambriento","جائع","affamé","hungry","emotions"),("thirsty","sediento","عطشان","assoiffé","thirsty","emotions"),("bored","aburrido","ممل","ennuyé","bored","emotions"),("proud","orgulloso","فخور","fier","proud","emotions"),("shy","tímido","خجول","timide","shy","emotions"),("calm","tranquilo","هادئ","calme","calm","emotions"),("love","amor","حب","amour","love","emotions"),("brave","valiente","شجاع","courageux","brave","emotions"),("run","correr","يركض","courir","running","actions"),("jump","saltar","يقفز","sauter","jumping","actions"),("walk","caminar","يمشي","marcher","walking","actions"),("swim","nadar","يسبح","nager","swimming","actions"),("fly","volar","يطير","voler","flying","actions"),("eat","comer","يأكل","manger","eating","actions"),("drink","beber","يشرب","boire","drinking","actions"),("sleep","dormir","ينام","dormir","sleeping","actions"),("read","leer","يقرأ","lire","reading","actions"),("write","escribir","يكتب","écrire","writing","actions"),("draw","dibujar","يرسم","dessiner","drawing","actions"),("sing","cantar","يغني","chanter","singing","actions"),("dance","bailar","يرقص","danser","dancing","actions"),("play","jugar","يلعب","jouer","playing","actions"),("laugh","reír","يضحك","rire","laughing","actions"),("cry","llorar","يبكي","pleurer","crying","actions"),("smile","sonreír","يبتسم","sourire","smiling","actions"),("talk","hablar","يتكلم","parler","talking","actions"),("help","ayudar","يساعد","aider","helping","actions"),("cook","cocinar","يطبخ","cuisiner","cooking","actions"),("big","grande","كبير","grand","big","adjectives"),("small","pequeño","صغير","petit","small","adjectives"),("tall","alto","طويل","grand/haut","tall","adjectives"),("fast","rápido","سريع","rapide","fast","adjectives"),("slow","lento","بطيء","lent","slow","adjectives"),("hot","caliente","ساخن","chaud","hot","adjectives"),("cold","frío","بارد","froid","cold","adjectives"),("hard","duro","صلب","dur","hard","adjectives"),("soft","suave","ناعم","doux","soft","adjectives"),("clean","limpio","نظيف","propre","clean","adjectives"),("dirty","sucio","وسخ","sale","dirty","adjectives"),("heavy","pesado","ثقيل","lourd","heavy","adjectives"),("light","ligero","خفيف","léger","light","adjectives"),("new","nuevo","جديد","nouveau","new","adjectives"),("old","viejo","قديم","vieux","old","adjectives"),("beautiful","hermoso","جميل","beau","beautiful","adjectives"),("strong","fuerte","قوي","fort","strong","adjectives"),("sweet","dulce","حلو","sucré","sweet","adjectives"),("sour","ácido","حامض","acide","sour","adjectives"),("loud","ruidoso","صاخب","bruyant","loud","adjectives"),("city","ciudad","مدينة","ville","city","places"),("park","parque","حديقة عامة","parc","park","places"),("market","mercado","سوق","marché","market","places"),("hospital","hospital","مستشفى","hôpital","hospital","places"),("restaurant","restaurante","مطعم","restaurant","restaurant","places"),("bakery","panadería","مخبزة","boulangerie","bakery","places"),("library","biblioteca","مكتبة","bibliothèque","library","places"),("museum","museo","متحف","musée","museum","places"),("zoo","zoo","حديقة الحيوانات","zoo","zoo","places"),("cinema","cine","سينما","cinéma","cinema","places"),("airport","aeropuerto","مطار","aéroport","airport","places"),("playground","parque infantil","ملعب","aire de jeux","playground","places"),("stadium","estadio","ملعب رياضي","stade","stadium","places"),("mosque","mezquita","مسجد","mosquée","mosque","places"),("farm","granja","مزرعة","ferme","farm","places"),("castle","castillo","قلعة","château","castle","places"),("bridge","puente","جسر","pont","bridge","places"),("lighthouse","faro","منارة","phare","lighthouse","places"),("fountain","fuente","نافورة","fontaine","fountain","places"),("statue","estatua","تمثال","statue","statue","places"),]
WORDS=[{"en":w[0],"es":w[1],"ar":w[2],"fr":w[3],"img":w[4],"cat":w[5]} for w in _W]

# ═══════════════════ WORD BANK ══════════════════════════════════
WORDS = [
    {"en":'apple',"es":'manzana',"ar":'تفاحة',"fr":'pomme',"img":'apple',"cat":'fruits'},
    {"en":'banana',"es":'plátano',"ar":'موزة',"fr":'banane',"img":'banana',"cat":'fruits'},
    {"en":'orange',"es":'naranja',"ar":'برتقالة',"fr":'orange',"img":'orange fruit',"cat":'fruits'},
    {"en":'strawberry',"es":'fresa',"ar":'فراولة',"fr":'fraise',"img":'strawberry',"cat":'fruits'},
    {"en":'grape',"es":'uva',"ar":'عنب',"fr":'raisin',"img":'grapes',"cat":'fruits'},
    {"en":'mango',"es":'mango',"ar":'مانجو',"fr":'mangue',"img":'mango',"cat":'fruits'},
    {"en":'watermelon',"es":'sandía',"ar":'بطيخ',"fr":'pastèque',"img":'watermelon',"cat":'fruits'},
    {"en":'pineapple',"es":'piña',"ar":'أناناس',"fr":'ananas',"img":'pineapple',"cat":'fruits'},
    {"en":'cherry',"es":'cereza',"ar":'كرز',"fr":'cerise',"img":'cherries',"cat":'fruits'},
    {"en":'peach',"es":'melocotón',"ar":'خوخ',"fr":'pêche',"img":'peach',"cat":'fruits'},
    {"en":'pear',"es":'pera',"ar":'كمثرى',"fr":'poire',"img":'pear',"cat":'fruits'},
    {"en":'lemon',"es":'limón',"ar":'ليمون',"fr":'citron',"img":'lemon',"cat":'fruits'},
    {"en":'coconut',"es":'coco',"ar":'جوز الهند',"fr":'noix de coco',"img":'coconut',"cat":'fruits'},
    {"en":'kiwi',"es":'kiwi',"ar":'كيوي',"fr":'kiwi',"img":'kiwi',"cat":'fruits'},
    {"en":'avocado',"es":'aguacate',"ar":'أفوكادو',"fr":'avocat',"img":'avocado',"cat":'fruits'},
    {"en":'blueberry',"es":'arándano',"ar":'توت أزرق',"fr":'myrtille',"img":'blueberries',"cat":'fruits'},
    {"en":'pomegranate',"es":'granada',"ar":'رمان',"fr":'grenade',"img":'pomegranate',"cat":'fruits'},
    {"en":'melon',"es":'melón',"ar":'شمام',"fr":'melon',"img":'melon',"cat":'fruits'},
    {"en":'tangerine',"es":'mandarina',"ar":'يوسفي',"fr":'mandarine',"img":'mandarine',"cat":'fruits'},
    {"en":'papaya',"es":'papaya',"ar":'بابايا',"fr":'papaye',"img":'papaya',"cat":'fruits'},
    {"en":'lime',"es":'lima',"ar":'ليمون أخضر',"fr":'citron vert',"img":'lime',"cat":'fruits'},
    {"en":'fig',"es":'higo',"ar":'تين',"fr":'figue',"img":'fig',"cat":'fruits'},
    {"en":'date',"es":'dátil',"ar":'تمر',"fr":'datte',"img":'dates fruit',"cat":'fruits'},
    {"en":'guava',"es":'guayaba',"ar":'جوافة',"fr":'goyave',"img":'guava',"cat":'fruits'},
    {"en":'passion fruit',"es":'maracuyá',"ar":'فاكهة الباشن',"fr":'fruit passion',"img":'passion fruit',"cat":'fruits'},
    {"en":'carrot',"es":'zanahoria',"ar":'جزرة',"fr":'carotte',"img":'carrot',"cat":'vegetables'},
    {"en":'tomato',"es":'tomate',"ar":'طماطم',"fr":'tomate',"img":'tomato',"cat":'vegetables'},
    {"en":'potato',"es":'patata',"ar":'بطاطا',"fr":'pomme de terre',"img":'potato',"cat":'vegetables'},
    {"en":'onion',"es":'cebolla',"ar":'بصلة',"fr":'oignon',"img":'onion',"cat":'vegetables'},
    {"en":'cucumber',"es":'pepino',"ar":'خيار',"fr":'concombre',"img":'cucumber',"cat":'vegetables'},
    {"en":'pepper',"es":'pimiento',"ar":'فلفل',"fr":'poivron',"img":'pepper',"cat":'vegetables'},
    {"en":'spinach',"es":'espinaca',"ar":'سبانخ',"fr":'épinard',"img":'spinach',"cat":'vegetables'},
    {"en":'broccoli',"es":'brócoli',"ar":'بروكلي',"fr":'brocoli',"img":'broccoli',"cat":'vegetables'},
    {"en":'corn',"es":'maíz',"ar":'ذرة',"fr":'maïs',"img":'corn',"cat":'vegetables'},
    {"en":'peas',"es":'guisantes',"ar":'بازلاء',"fr":'petits pois',"img":'peas',"cat":'vegetables'},
    {"en":'lettuce',"es":'lechuga',"ar":'خس',"fr":'laitue',"img":'lettuce',"cat":'vegetables'},
    {"en":'mushroom',"es":'champiñón',"ar":'فطر',"fr":'champignon',"img":'mushroom',"cat":'vegetables'},
    {"en":'eggplant',"es":'berenjena',"ar":'باذنجان',"fr":'aubergine',"img":'eggplant',"cat":'vegetables'},
    {"en":'zucchini',"es":'calabacín',"ar":'كوسة',"fr":'courgette',"img":'zucchini',"cat":'vegetables'},
    {"en":'garlic',"es":'ajo',"ar":'ثوم',"fr":'ail',"img":'garlic',"cat":'vegetables'},
    {"en":'pumpkin',"es":'calabaza',"ar":'قرع',"fr":'citrouille',"img":'pumpkin',"cat":'vegetables'},
    {"en":'cabbage',"es":'col',"ar":'كرنب',"fr":'chou',"img":'cabbage',"cat":'vegetables'},
    {"en":'sweet potato',"es":'boniato',"ar":'بطاطا حلوة',"fr":'patate douce',"img":'sweet potato',"cat":'vegetables'},
    {"en":'cauliflower',"es":'coliflor',"ar":'قرنبيط',"fr":'chou-fleur',"img":'cauliflower',"cat":'vegetables'},
    {"en":'asparagus',"es":'espárrago',"ar":'هليون',"fr":'asperge',"img":'asparagus',"cat":'vegetables'},
    {"en":'beetroot',"es":'remolacha',"ar":'شمندر',"fr":'betterave',"img":'beetroot',"cat":'vegetables'},
    {"en":'cat',"es":'gato',"ar":'قطة',"fr":'chat',"img":'cat',"cat":'animals'},
    {"en":'dog',"es":'perro',"ar":'كلب',"fr":'chien',"img":'dog',"cat":'animals'},
    {"en":'rabbit',"es":'conejo',"ar":'أرنب',"fr":'lapin',"img":'rabbit',"cat":'animals'},
    {"en":'hamster',"es":'hámster',"ar":'هامستر',"fr":'hamster',"img":'hamster',"cat":'animals'},
    {"en":'parrot',"es":'loro',"ar":'ببغاء',"fr":'perroquet',"img":'parrot',"cat":'animals'},
    {"en":'goldfish',"es":'pez dorado',"ar":'سمكة ذهبية',"fr":'poisson rouge',"img":'goldfish',"cat":'animals'},
    {"en":'turtle',"es":'tortuga',"ar":'سلحفاة',"fr":'tortue',"img":'turtle',"cat":'animals'},
    {"en":'horse',"es":'caballo',"ar":'حصان',"fr":'cheval',"img":'horse',"cat":'animals'},
    {"en":'cow',"es":'vaca',"ar":'بقرة',"fr":'vache',"img":'cow',"cat":'animals'},
    {"en":'sheep',"es":'oveja',"ar":'خروف',"fr":'mouton',"img":'sheep',"cat":'animals'},
    {"en":'goat',"es":'cabra',"ar":'ماعز',"fr":'chèvre',"img":'goat',"cat":'animals'},
    {"en":'chicken',"es":'gallina',"ar":'دجاجة',"fr":'poule',"img":'chicken',"cat":'animals'},
    {"en":'duck',"es":'pato',"ar":'بطة',"fr":'canard',"img":'duck',"cat":'animals'},
    {"en":'donkey',"es":'burro',"ar":'حمار',"fr":'âne',"img":'donkey',"cat":'animals'},
    {"en":'mouse',"es":'ratón',"ar":'فأر',"fr":'souris',"img":'mouse',"cat":'animals'},
    {"en":'guinea pig',"es":'cobaya',"ar":'خنزير غيني',"fr":'cobaye',"img":'guinea pig',"cat":'animals'},
    {"en":'canary',"es":'canario',"ar":'كناري',"fr":'canari',"img":'canary',"cat":'animals'},
    {"en":'rooster',"es":'gallo',"ar":'ديك',"fr":'coq',"img":'rooster',"cat":'animals'},
    {"en":'lion',"es":'león',"ar":'أسد',"fr":'lion',"img":'lion',"cat":'wild_animals'},
    {"en":'tiger',"es":'tigre',"ar":'نمر',"fr":'tigre',"img":'tiger',"cat":'wild_animals'},
    {"en":'elephant',"es":'elefante',"ar":'فيل',"fr":'éléphant',"img":'elephant',"cat":'wild_animals'},
    {"en":'giraffe',"es":'jirafa',"ar":'زرافة',"fr":'girafe',"img":'giraffe',"cat":'wild_animals'},
    {"en":'zebra',"es":'cebra',"ar":'حمار وحشي',"fr":'zèbre',"img":'zebra',"cat":'wild_animals'},
    {"en":'monkey',"es":'mono',"ar":'قرد',"fr":'singe',"img":'monkey',"cat":'wild_animals'},
    {"en":'gorilla',"es":'gorila',"ar":'غوريلا',"fr":'gorille',"img":'gorilla',"cat":'wild_animals'},
    {"en":'bear',"es":'oso',"ar":'دب',"fr":'ours',"img":'bear',"cat":'wild_animals'},
    {"en":'wolf',"es":'lobo',"ar":'ذئب',"fr":'loup',"img":'wolf',"cat":'wild_animals'},
    {"en":'fox',"es":'zorro',"ar":'ثعلب',"fr":'renard',"img":'fox',"cat":'wild_animals'},
    {"en":'deer',"es":'ciervo',"ar":'غزال',"fr":'cerf',"img":'deer',"cat":'wild_animals'},
    {"en":'crocodile',"es":'cocodrilo',"ar":'تمساح',"fr":'crocodile',"img":'crocodile',"cat":'wild_animals'},
    {"en":'hippopotamus',"es":'hipopótamo',"ar":'فرس البحر',"fr":'hippopotame',"img":'hippo',"cat":'wild_animals'},
    {"en":'rhinoceros',"es":'rinoceronte',"ar":'وحيد القرن',"fr":'rhinocéros',"img":'rhinoceros',"cat":'wild_animals'},
    {"en":'cheetah',"es":'guepardo',"ar":'فهد',"fr":'guépard',"img":'cheetah',"cat":'wild_animals'},
    {"en":'kangaroo',"es":'canguro',"ar":'كنغر',"fr":'kangourou',"img":'kangaroo',"cat":'wild_animals'},
    {"en":'koala',"es":'koala',"ar":'كوالا',"fr":'koala',"img":'koala',"cat":'wild_animals'},
    {"en":'panda',"es":'panda',"ar":'باندا',"fr":'panda',"img":'panda',"cat":'wild_animals'},
    {"en":'polar bear',"es":'oso polar',"ar":'دب قطبي',"fr":'ours polaire',"img":'polar bear',"cat":'wild_animals'},
    {"en":'camel',"es":'camello',"ar":'جمل',"fr":'chameau',"img":'camel',"cat":'wild_animals'},
    {"en":'snake',"es":'serpiente',"ar":'ثعبان',"fr":'serpent',"img":'snake',"cat":'wild_animals'},
    {"en":'frog',"es":'rana',"ar":'ضفدع',"fr":'grenouille',"img":'frog',"cat":'wild_animals'},
    {"en":'squirrel',"es":'ardilla',"ar":'سنجاب',"fr":'écureuil',"img":'squirrel',"cat":'wild_animals'},
    {"en":'hedgehog',"es":'erizo',"ar":'قنفذ',"fr":'hérisson',"img":'hedgehog',"cat":'wild_animals'},
    {"en":'penguin',"es":'pingüino',"ar":'بطريق',"fr":'pingouin',"img":'penguin',"cat":'wild_animals'},
    {"en":'dolphin',"es":'delfín',"ar":'دلفين',"fr":'dauphin',"img":'dolphin',"cat":'sea'},
    {"en":'whale',"es":'ballena',"ar":'حوت',"fr":'baleine',"img":'whale',"cat":'sea'},
    {"en":'shark',"es":'tiburón',"ar":'قرش',"fr":'requin',"img":'shark',"cat":'sea'},
    {"en":'octopus',"es":'pulpo',"ar":'أخطبوط',"fr":'pieuvre',"img":'octopus',"cat":'sea'},
    {"en":'crab',"es":'cangrejo',"ar":'سرطان البحر',"fr":'crabe',"img":'crab',"cat":'sea'},
    {"en":'seahorse',"es":'caballito de mar',"ar":'أبو رمال',"fr":'hippocampe',"img":'seahorse',"cat":'sea'},
    {"en":'starfish',"es":'estrella de mar',"ar":'نجم البحر',"fr":'étoile de mer',"img":'starfish',"cat":'sea'},
    {"en":'jellyfish',"es":'medusa',"ar":'قنديل البحر',"fr":'méduse',"img":'jellyfish',"cat":'sea'},
    {"en":'lobster',"es":'langosta',"ar":'كركند',"fr":'homard',"img":'lobster',"cat":'sea'},
    {"en":'clownfish',"es":'pez payaso',"ar":'سمكة مهرج',"fr":'poisson clown',"img":'clownfish',"cat":'sea'},
    {"en":'seal',"es":'foca',"ar":'فقمة',"fr":'phoque',"img":'seal',"cat":'sea'},
    {"en":'eagle',"es":'águila',"ar":'نسر',"fr":'aigle',"img":'eagle',"cat":'birds'},
    {"en":'owl',"es":'búho',"ar":'بوم',"fr":'hibou',"img":'owl',"cat":'birds'},
    {"en":'flamingo',"es":'flamenco',"ar":'نحام',"fr":'flamant rose',"img":'flamingo',"cat":'birds'},
    {"en":'peacock',"es":'pavo real',"ar":'طاووس',"fr":'paon',"img":'peacock',"cat":'birds'},
    {"en":'toucan',"es":'tucán',"ar":'طوقان',"fr":'toucan',"img":'toucan',"cat":'birds'},
    {"en":'hummingbird',"es":'colibrí',"ar":'طائر طنان',"fr":'colibri',"img":'hummingbird',"cat":'birds'},
    {"en":'sparrow',"es":'gorrión',"ar":'عصفور',"fr":'moineau',"img":'sparrow',"cat":'birds'},
    {"en":'swan',"es":'cisne',"ar":'بجعة',"fr":'cygne',"img":'swan',"cat":'birds'},
    {"en":'butterfly',"es":'mariposa',"ar":'فراشة',"fr":'papillon',"img":'butterfly',"cat":'insects'},
    {"en":'bee',"es":'abeja',"ar":'نحلة',"fr":'abeille',"img":'bee',"cat":'insects'},
    {"en":'ladybug',"es":'mariquita',"ar":'دعسوقة',"fr":'coccinelle',"img":'ladybug',"cat":'insects'},
    {"en":'ant',"es":'hormiga',"ar":'نملة',"fr":'fourmi',"img":'ant',"cat":'insects'},
    {"en":'bread',"es":'pan',"ar":'خبز',"fr":'pain',"img":'bread',"cat":'food'},
    {"en":'rice',"es":'arroz',"ar":'أرز',"fr":'riz',"img":'rice',"cat":'food'},
    {"en":'pasta',"es":'pasta',"ar":'مكرونة',"fr":'pâtes',"img":'pasta',"cat":'food'},
    {"en":'pizza',"es":'pizza',"ar":'بيتزا',"fr":'pizza',"img":'pizza',"cat":'food'},
    {"en":'soup',"es":'sopa',"ar":'شوربة',"fr":'soupe',"img":'soup',"cat":'food'},
    {"en":'egg',"es":'huevo',"ar":'بيضة',"fr":'œuf',"img":'egg',"cat":'food'},
    {"en":'cheese',"es":'queso',"ar":'جبن',"fr":'fromage',"img":'cheese',"cat":'food'},
    {"en":'butter',"es":'mantequilla',"ar":'زبدة',"fr":'beurre',"img":'butter',"cat":'food'},
    {"en":'honey',"es":'miel',"ar":'عسل',"fr":'miel',"img":'honey',"cat":'food'},
    {"en":'sandwich',"es":'sándwich',"ar":'ساندويتش',"fr":'sandwich',"img":'sandwich',"cat":'food'},
    {"en":'hamburger',"es":'hamburguesa',"ar":'همبرغر',"fr":'hamburger',"img":'hamburger',"cat":'food'},
    {"en":'cake',"es":'pastel',"ar":'كعكة',"fr":'gâteau',"img":'cake',"cat":'food'},
    {"en":'cookie',"es":'galleta',"ar":'كوكيز',"fr":'biscuit',"img":'cookie',"cat":'food'},
    {"en":'ice cream',"es":'helado',"ar":'آيس كريم',"fr":'glace',"img":'ice cream',"cat":'food'},
    {"en":'chocolate',"es":'chocolate',"ar":'شوكولاتة',"fr":'chocolat',"img":'chocolate',"cat":'food'},
    {"en":'chips',"es":'patatas fritas',"ar":'رقائق',"fr":'chips',"img":'chips',"cat":'food'},
    {"en":'popcorn',"es":'palomitas',"ar":'فشار',"fr":'popcorn',"img":'popcorn',"cat":'food'},
    {"en":'candy',"es":'caramelo',"ar":'حلوى',"fr":'bonbon',"img":'candy',"cat":'food'},
    {"en":'jam',"es":'mermelada',"ar":'مربى',"fr":'confiture',"img":'jam',"cat":'food'},
    {"en":'yogurt',"es":'yogur',"ar":'زبادي',"fr":'yaourt',"img":'yogurt',"cat":'food'},
    {"en":'pancake',"es":'tortita',"ar":'فطيرة',"fr":'crêpe',"img":'pancake',"cat":'food'},
    {"en":'croissant',"es":'croissant',"ar":'كرواسان',"fr":'croissant',"img":'croissant',"cat":'food'},
    {"en":'donut',"es":'donut',"ar":'دونات',"fr":'donut',"img":'donut',"cat":'food'},
    {"en":'salad',"es":'ensalada',"ar":'سلطة',"fr":'salade',"img":'salad',"cat":'food'},
    {"en":'meat',"es":'carne',"ar":'لحم',"fr":'viande',"img":'meat',"cat":'food'},
    {"en":'waffle',"es":'gofre',"ar":'وافل',"fr":'gaufre',"img":'waffle',"cat":'food'},
    {"en":'water',"es":'agua',"ar":'ماء',"fr":'eau',"img":'water',"cat":'drinks'},
    {"en":'milk',"es":'leche',"ar":'حليب',"fr":'lait',"img":'milk',"cat":'drinks'},
    {"en":'juice',"es":'zumo',"ar":'عصير',"fr":'jus',"img":'juice',"cat":'drinks'},
    {"en":'tea',"es":'té',"ar":'شاي',"fr":'thé',"img":'tea',"cat":'drinks'},
    {"en":'coffee',"es":'café',"ar":'قهوة',"fr":'café',"img":'coffee',"cat":'drinks'},
    {"en":'lemonade',"es":'limonada',"ar":'ليمونادة',"fr":'limonade',"img":'lemonade',"cat":'drinks'},
    {"en":'smoothie',"es":'batido',"ar":'عصير سموذي',"fr":'smoothie',"img":'smoothie',"cat":'drinks'},
    {"en":'hot chocolate',"es":'chocolate caliente',"ar":'شوكولاتة ساخنة',"fr":'chocolat chaud',"img":'hot chocolate',"cat":'drinks'},
    {"en":'mint tea',"es":'té de menta',"ar":'شاي بالنعناع',"fr":'thé à la menthe',"img":'mint tea',"cat":'drinks'},
    {"en":'milkshake',"es":'batido de leche',"ar":'ميلك شيك',"fr":'milkshake',"img":'milkshake',"cat":'drinks'},
    {"en":'head',"es":'cabeza',"ar":'رأس',"fr":'tête',"img":'head',"cat":'body'},
    {"en":'hair',"es":'pelo',"ar":'شعر',"fr":'cheveux',"img":'hair',"cat":'body'},
    {"en":'eye',"es":'ojo',"ar":'عين',"fr":'œil',"img":'eye',"cat":'body'},
    {"en":'ear',"es":'oreja',"ar":'أذن',"fr":'oreille',"img":'ear',"cat":'body'},
    {"en":'nose',"es":'nariz',"ar":'أنف',"fr":'nez',"img":'nose',"cat":'body'},
    {"en":'mouth',"es":'boca',"ar":'فم',"fr":'bouche',"img":'mouth',"cat":'body'},
    {"en":'tooth',"es":'diente',"ar":'سن',"fr":'dent',"img":'teeth',"cat":'body'},
    {"en":'hand',"es":'mano',"ar":'يد',"fr":'main',"img":'hand',"cat":'body'},
    {"en":'finger',"es":'dedo',"ar":'إصبع',"fr":'doigt',"img":'finger',"cat":'body'},
    {"en":'arm',"es":'brazo',"ar":'ذراع',"fr":'bras',"img":'arm',"cat":'body'},
    {"en":'leg',"es":'pierna',"ar":'ساق',"fr":'jambe',"img":'leg',"cat":'body'},
    {"en":'foot',"es":'pie',"ar":'قدم',"fr":'pied',"img":'foot',"cat":'body'},
    {"en":'shoulder',"es":'hombro',"ar":'كتف',"fr":'épaule',"img":'shoulder',"cat":'body'},
    {"en":'knee',"es":'rodilla',"ar":'ركبة',"fr":'genou',"img":'knee',"cat":'body'},
    {"en":'heart',"es":'corazón',"ar":'قلب',"fr":'cœur',"img":'heart',"cat":'body'},
    {"en":'brain',"es":'cerebro',"ar":'مخ',"fr":'cerveau',"img":'brain',"cat":'body'},
    {"en":'muscle',"es":'músculo',"ar":'عضلة',"fr":'muscle',"img":'muscle',"cat":'body'},
    {"en":'red',"es":'rojo',"ar":'أحمر',"fr":'rouge',"img":'red',"cat":'colors'},
    {"en":'blue',"es":'azul',"ar":'أزرق',"fr":'bleu',"img":'blue',"cat":'colors'},
    {"en":'yellow',"es":'amarillo',"ar":'أصفر',"fr":'jaune',"img":'yellow',"cat":'colors'},
    {"en":'green',"es":'verde',"ar":'أخضر',"fr":'vert',"img":'green',"cat":'colors'},
    {"en":'orange',"es":'naranja',"ar":'برتقالي',"fr":'orange',"img":'orange color',"cat":'colors'},
    {"en":'purple',"es":'morado',"ar":'بنفسجي',"fr":'violet',"img":'purple',"cat":'colors'},
    {"en":'pink',"es":'rosa',"ar":'وردي',"fr":'rose',"img":'pink',"cat":'colors'},
    {"en":'black',"es":'negro',"ar":'أسود',"fr":'noir',"img":'black',"cat":'colors'},
    {"en":'white',"es":'blanco',"ar":'أبيض',"fr":'blanc',"img":'white',"cat":'colors'},
    {"en":'brown',"es":'marrón',"ar":'بني',"fr":'marron',"img":'brown',"cat":'colors'},
    {"en":'grey',"es":'gris',"ar":'رمادي',"fr":'gris',"img":'grey',"cat":'colors'},
    {"en":'shirt',"es":'camisa',"ar":'قميص',"fr":'chemise',"img":'shirt',"cat":'clothes'},
    {"en":'t-shirt',"es":'camiseta',"ar":'تيشيرت',"fr":'t-shirt',"img":'t-shirt',"cat":'clothes'},
    {"en":'dress',"es":'vestido',"ar":'فستان',"fr":'robe',"img":'dress',"cat":'clothes'},
    {"en":'pants',"es":'pantalón',"ar":'بنطلون',"fr":'pantalon',"img":'pants',"cat":'clothes'},
    {"en":'jacket',"es":'chaqueta',"ar":'جاكيت',"fr":'veste',"img":'jacket',"cat":'clothes'},
    {"en":'coat',"es":'abrigo',"ar":'معطف',"fr":'manteau',"img":'coat',"cat":'clothes'},
    {"en":'sweater',"es":'suéter',"ar":'بلوزة',"fr":'pull',"img":'sweater',"cat":'clothes'},
    {"en":'shoes',"es":'zapatos',"ar":'أحذية',"fr":'chaussures',"img":'shoes',"cat":'clothes'},
    {"en":'boots',"es":'botas',"ar":'حذاء بوت',"fr":'bottes',"img":'boots',"cat":'clothes'},
    {"en":'sneakers',"es":'zapatillas',"ar":'حذاء رياضي',"fr":'baskets',"img":'sneakers',"cat":'clothes'},
    {"en":'sandals',"es":'sandalias',"ar":'صندل',"fr":'sandales',"img":'sandals',"cat":'clothes'},
    {"en":'socks',"es":'calcetines',"ar":'جوارب',"fr":'chaussettes',"img":'socks',"cat":'clothes'},
    {"en":'hat',"es":'sombrero',"ar":'قبعة',"fr":'chapeau',"img":'hat',"cat":'clothes'},
    {"en":'cap',"es":'gorra',"ar":'طاقية',"fr":'casquette',"img":'cap',"cat":'clothes'},
    {"en":'scarf',"es":'bufanda',"ar":'وشاح',"fr":'écharpe',"img":'scarf',"cat":'clothes'},
    {"en":'gloves',"es":'guantes',"ar":'قفازات',"fr":'gants',"img":'gloves',"cat":'clothes'},
    {"en":'pajamas',"es":'pijama',"ar":'بيجاما',"fr":'pyjama',"img":'pajamas',"cat":'clothes'},
    {"en":'swimsuit',"es":'bañador',"ar":'ملابس سباحة',"fr":'maillot de bain',"img":'swimsuit',"cat":'clothes'},
    {"en":'raincoat',"es":'impermeable',"ar":'معطف مطر',"fr":'imperméable',"img":'raincoat',"cat":'clothes'},
    {"en":'house',"es":'casa',"ar":'بيت',"fr":'maison',"img":'house',"cat":'home'},
    {"en":'door',"es":'puerta',"ar":'باب',"fr":'porte',"img":'door',"cat":'home'},
    {"en":'window',"es":'ventana',"ar":'نافذة',"fr":'fenêtre',"img":'window',"cat":'home'},
    {"en":'kitchen',"es":'cocina',"ar":'مطبخ',"fr":'cuisine',"img":'kitchen',"cat":'home'},
    {"en":'bedroom',"es":'dormitorio',"ar":'غرفة نوم',"fr":'chambre',"img":'bedroom',"cat":'home'},
    {"en":'bathroom',"es":'baño',"ar":'حمام',"fr":'salle de bain',"img":'bathroom',"cat":'home'},
    {"en":'living room',"es":'sala de estar',"ar":'غرفة معيشة',"fr":'salon',"img":'living room',"cat":'home'},
    {"en":'bed',"es":'cama',"ar":'سرير',"fr":'lit',"img":'bed',"cat":'home'},
    {"en":'chair',"es":'silla',"ar":'كرسي',"fr":'chaise',"img":'chair',"cat":'home'},
    {"en":'table',"es":'mesa',"ar":'طاولة',"fr":'table',"img":'table',"cat":'home'},
    {"en":'sofa',"es":'sofá',"ar":'أريكة',"fr":'canapé',"img":'sofa',"cat":'home'},
    {"en":'lamp',"es":'lámpara',"ar":'مصباح',"fr":'lampe',"img":'lamp',"cat":'home'},
    {"en":'fridge',"es":'nevera',"ar":'ثلاجة',"fr":'réfrigérateur',"img":'fridge',"cat":'home'},
    {"en":'oven',"es":'horno',"ar":'فرن',"fr":'four',"img":'oven',"cat":'home'},
    {"en":'shower',"es":'ducha',"ar":'دش',"fr":'douche',"img":'shower',"cat":'home'},
    {"en":'television',"es":'televisión',"ar":'تلفاز',"fr":'télévision',"img":'tv',"cat":'home'},
    {"en":'garden',"es":'jardín',"ar":'حديقة',"fr":'jardin',"img":'garden',"cat":'home'},
    {"en":'stairs',"es":'escaleras',"ar":'سلم',"fr":'escalier',"img":'stairs',"cat":'home'},
    {"en":'school',"es":'escuela',"ar":'مدرسة',"fr":'école',"img":'school',"cat":'school'},
    {"en":'classroom',"es":'aula',"ar":'فصل دراسي',"fr":'salle de classe',"img":'classroom',"cat":'school'},
    {"en":'teacher',"es":'profesor',"ar":'معلم',"fr":'professeur',"img":'teacher',"cat":'school'},
    {"en":'book',"es":'libro',"ar":'كتاب',"fr":'livre',"img":'book',"cat":'school'},
    {"en":'notebook',"es":'cuaderno',"ar":'دفتر',"fr":'cahier',"img":'notebook',"cat":'school'},
    {"en":'pencil',"es":'lápiz',"ar":'قلم رصاص',"fr":'crayon',"img":'pencil',"cat":'school'},
    {"en":'pen',"es":'bolígrafo',"ar":'قلم',"fr":'stylo',"img":'pen',"cat":'school'},
    {"en":'eraser',"es":'goma',"ar":'ممحاة',"fr":'gomme',"img":'eraser',"cat":'school'},
    {"en":'ruler',"es":'regla',"ar":'مسطرة',"fr":'règle',"img":'ruler',"cat":'school'},
    {"en":'scissors',"es":'tijeras',"ar":'مقص',"fr":'ciseaux',"img":'scissors',"cat":'school'},
    {"en":'glue',"es":'pegamento',"ar":'غراء',"fr":'colle',"img":'glue',"cat":'school'},
    {"en":'backpack',"es":'mochila',"ar":'حقيبة مدرسية',"fr":'cartable',"img":'backpack',"cat":'school'},
    {"en":'board',"es":'pizarra',"ar":'سبورة',"fr":'tableau',"img":'blackboard',"cat":'school'},
    {"en":'calculator',"es":'calculadora',"ar":'آلة حاسبة',"fr":'calculatrice',"img":'calculator',"cat":'school'},
    {"en":'globe',"es":'globo terráqueo',"ar":'كرة الأرض',"fr":'globe terrestre',"img":'globe',"cat":'school'},
    {"en":'map',"es":'mapa',"ar":'خريطة',"fr":'carte',"img":'map',"cat":'school'},
    {"en":'car',"es":'coche',"ar":'سيارة',"fr":'voiture',"img":'car',"cat":'transport'},
    {"en":'bus',"es":'autobús',"ar":'حافلة',"fr":'bus',"img":'bus',"cat":'transport'},
    {"en":'train',"es":'tren',"ar":'قطار',"fr":'train',"img":'train',"cat":'transport'},
    {"en":'airplane',"es":'avión',"ar":'طائرة',"fr":'avion',"img":'airplane',"cat":'transport'},
    {"en":'boat',"es":'barco',"ar":'قارب',"fr":'bateau',"img":'boat',"cat":'transport'},
    {"en":'bicycle',"es":'bicicleta',"ar":'دراجة',"fr":'vélo',"img":'bicycle',"cat":'transport'},
    {"en":'motorcycle',"es":'moto',"ar":'دراجة نارية',"fr":'moto',"img":'motorcycle',"cat":'transport'},
    {"en":'truck',"es":'camión',"ar":'شاحنة',"fr":'camion',"img":'truck',"cat":'transport'},
    {"en":'ambulance',"es":'ambulancia',"ar":'سيارة إسعاف',"fr":'ambulance',"img":'ambulance',"cat":'transport'},
    {"en":'helicopter',"es":'helicóptero',"ar":'طائرة مروحية',"fr":'hélicoptère',"img":'helicopter',"cat":'transport'},
    {"en":'taxi',"es":'taxi',"ar":'تاكسي',"fr":'taxi',"img":'taxi',"cat":'transport'},
    {"en":'scooter',"es":'patinete',"ar":'سكوتر',"fr":'trottinette',"img":'scooter',"cat":'transport'},
    {"en":'rocket',"es":'cohete',"ar":'صاروخ',"fr":'fusée',"img":'rocket',"cat":'transport'},
    {"en":'sun',"es":'sol',"ar":'شمس',"fr":'soleil',"img":'sun',"cat":'nature'},
    {"en":'moon',"es":'luna',"ar":'قمر',"fr":'lune',"img":'moon',"cat":'nature'},
    {"en":'star',"es":'estrella',"ar":'نجمة',"fr":'étoile',"img":'star',"cat":'nature'},
    {"en":'cloud',"es":'nube',"ar":'سحابة',"fr":'nuage',"img":'cloud',"cat":'nature'},
    {"en":'rain',"es":'lluvia',"ar":'مطر',"fr":'pluie',"img":'rain',"cat":'nature'},
    {"en":'snow',"es":'nieve',"ar":'ثلج',"fr":'neige',"img":'snow',"cat":'nature'},
    {"en":'rainbow',"es":'arcoíris',"ar":'قوس قزح',"fr":'arc-en-ciel',"img":'rainbow',"cat":'nature'},
    {"en":'tree',"es":'árbol',"ar":'شجرة',"fr":'arbre',"img":'tree',"cat":'nature'},
    {"en":'flower',"es":'flor',"ar":'زهرة',"fr":'fleur',"img":'flower',"cat":'nature'},
    {"en":'river',"es":'río',"ar":'نهر',"fr":'rivière',"img":'river',"cat":'nature'},
    {"en":'ocean',"es":'océano',"ar":'محيط',"fr":'océan',"img":'ocean',"cat":'nature'},
    {"en":'mountain',"es":'montaña',"ar":'جبل',"fr":'montagne',"img":'mountain',"cat":'nature'},
    {"en":'desert',"es":'desierto',"ar":'صحراء',"fr":'désert',"img":'desert',"cat":'nature'},
    {"en":'forest',"es":'bosque',"ar":'غابة',"fr":'forêt',"img":'forest',"cat":'nature'},
    {"en":'beach',"es":'playa',"ar":'شاطئ',"fr":'plage',"img":'beach',"cat":'nature'},
    {"en":'lake',"es":'lago',"ar":'بحيرة',"fr":'lac',"img":'lake',"cat":'nature'},
    {"en":'spring',"es":'primavera',"ar":'ربيع',"fr":'printemps',"img":'spring',"cat":'nature'},
    {"en":'summer',"es":'verano',"ar":'صيف',"fr":'été',"img":'summer',"cat":'nature'},
    {"en":'autumn',"es":'otoño',"ar":'خريف',"fr":'automne',"img":'autumn',"cat":'nature'},
    {"en":'winter',"es":'invierno',"ar":'شتاء',"fr":'hiver',"img":'winter',"cat":'nature'},
    {"en":'wind',"es":'viento',"ar":'ريح',"fr":'vent',"img":'wind',"cat":'nature'},
    {"en":'volcano',"es":'volcán',"ar":'بركان',"fr":'volcan',"img":'volcano',"cat":'nature'},
    {"en":'island',"es":'isla',"ar":'جزيرة',"fr":'île',"img":'island',"cat":'nature'},
    {"en":'waterfall',"es":'cascada',"ar":'شلال',"fr":'cascade',"img":'waterfall',"cat":'nature'},
    {"en":'mother',"es":'madre',"ar":'أم',"fr":'mère',"img":'mother',"cat":'family'},
    {"en":'father',"es":'padre',"ar":'أب',"fr":'père',"img":'father',"cat":'family'},
    {"en":'sister',"es":'hermana',"ar":'أخت',"fr":'sœur',"img":'sisters',"cat":'family'},
    {"en":'brother',"es":'hermano',"ar":'أخ',"fr":'frère',"img":'brothers',"cat":'family'},
    {"en":'grandmother',"es":'abuela',"ar":'جدة',"fr":'grand-mère',"img":'grandmother',"cat":'family'},
    {"en":'grandfather',"es":'abuelo',"ar":'جد',"fr":'grand-père',"img":'grandfather',"cat":'family'},
    {"en":'baby',"es":'bebé',"ar":'رضيع',"fr":'bébé',"img":'baby',"cat":'family'},
    {"en":'girl',"es":'niña',"ar":'بنت',"fr":'fille',"img":'girl',"cat":'family'},
    {"en":'boy',"es":'niño',"ar":'ولد',"fr":'garçon',"img":'boy',"cat":'family'},
    {"en":'friend',"es":'amigo',"ar":'صديق',"fr":'ami',"img":'friends',"cat":'family'},
    {"en":'doctor',"es":'médico',"ar":'طبيب',"fr":'médecin',"img":'doctor',"cat":'family'},
    {"en":'nurse',"es":'enfermera',"ar":'ممرضة',"fr":'infirmière',"img":'nurse',"cat":'family'},
    {"en":'police',"es":'policía',"ar":'شرطي',"fr":'policier',"img":'police',"cat":'family'},
    {"en":'firefighter',"es":'bombero',"ar":'إطفائي',"fr":'pompier',"img":'firefighter',"cat":'family'},
    {"en":'chef',"es":'cocinero',"ar":'طاهٍ',"fr":'chef cuisinier',"img":'chef',"cat":'family'},
    {"en":'farmer',"es":'agricultor',"ar":'مزارع',"fr":'agriculteur',"img":'farmer',"cat":'family'},
    {"en":'pilot',"es":'piloto',"ar":'طيار',"fr":'pilote',"img":'pilot',"cat":'family'},
    {"en":'astronaut',"es":'astronauta',"ar":'رائد فضاء',"fr":'astronaute',"img":'astronaut',"cat":'family'},
    {"en":'football',"es":'fútbol',"ar":'كرة القدم',"fr":'football',"img":'football',"cat":'sports'},
    {"en":'basketball',"es":'baloncesto',"ar":'كرة السلة',"fr":'basketball',"img":'basketball',"cat":'sports'},
    {"en":'tennis',"es":'tenis',"ar":'تنس',"fr":'tennis',"img":'tennis',"cat":'sports'},
    {"en":'swimming',"es":'natación',"ar":'سباحة',"fr":'natation',"img":'swimming',"cat":'sports'},
    {"en":'cycling',"es":'ciclismo',"ar":'ركوب الدراجة',"fr":'cyclisme',"img":'cycling',"cat":'sports'},
    {"en":'running',"es":'correr',"ar":'الجري',"fr":'course',"img":'running',"cat":'sports'},
    {"en":'gymnastics',"es":'gimnasia',"ar":'جمباز',"fr":'gymnastique',"img":'gymnastics',"cat":'sports'},
    {"en":'skiing',"es":'esquí',"ar":'تزلج',"fr":'ski',"img":'skiing',"cat":'sports'},
    {"en":'surfing',"es":'surf',"ar":'ركوب الأمواج',"fr":'surf',"img":'surfing',"cat":'sports'},
    {"en":'boxing',"es":'boxeo',"ar":'ملاكمة',"fr":'boxe',"img":'boxing',"cat":'sports'},
    {"en":'chess',"es":'ajedrez',"ar":'شطرنج',"fr":'échecs',"img":'chess',"cat":'sports'},
    {"en":'puzzle',"es":'puzzle',"ar":'أحجية',"fr":'puzzle',"img":'puzzle',"cat":'sports'},
    {"en":'kite',"es":'cometa',"ar":'طائرة ورقية',"fr":'cerf-volant',"img":'kite',"cat":'sports'},
    {"en":'trampoline',"es":'trampolín',"ar":'ترامبولين',"fr":'trampoline',"img":'trampoline',"cat":'sports'},
    {"en":'bowling',"es":'bolos',"ar":'بولينغ',"fr":'bowling',"img":'bowling',"cat":'sports'},
    {"en":'ping pong',"es":'ping-pong',"ar":'تنس طاولة',"fr":'ping-pong',"img":'ping pong',"cat":'sports'},
    {"en":'happy',"es":'feliz',"ar":'سعيد',"fr":'heureux',"img":'happy',"cat":'emotions'},
    {"en":'sad',"es":'triste',"ar":'حزين',"fr":'triste',"img":'sad',"cat":'emotions'},
    {"en":'angry',"es":'enfadado',"ar":'غاضب',"fr":'en colère',"img":'angry',"cat":'emotions'},
    {"en":'scared',"es":'asustado',"ar":'خائف',"fr":'effrayé',"img":'scared',"cat":'emotions'},
    {"en":'surprised',"es":'sorprendido',"ar":'مندهش',"fr":'surpris',"img":'surprised',"cat":'emotions'},
    {"en":'excited',"es":'emocionado',"ar":'متحمس',"fr":'excité',"img":'excited',"cat":'emotions'},
    {"en":'tired',"es":'cansado',"ar":'متعب',"fr":'fatigué',"img":'tired',"cat":'emotions'},
    {"en":'hungry',"es":'hambriento',"ar":'جائع',"fr":'affamé',"img":'hungry',"cat":'emotions'},
    {"en":'thirsty',"es":'sediento',"ar":'عطشان',"fr":'assoiffé',"img":'thirsty',"cat":'emotions'},
    {"en":'bored',"es":'aburrido',"ar":'ممل',"fr":'ennuyé',"img":'bored',"cat":'emotions'},
    {"en":'proud',"es":'orgulloso',"ar":'فخور',"fr":'fier',"img":'proud',"cat":'emotions'},
    {"en":'shy',"es":'tímido',"ar":'خجول',"fr":'timide',"img":'shy',"cat":'emotions'},
    {"en":'calm',"es":'tranquilo',"ar":'هادئ',"fr":'calme',"img":'calm',"cat":'emotions'},
    {"en":'love',"es":'amor',"ar":'حب',"fr":'amour',"img":'love',"cat":'emotions'},
    {"en":'brave',"es":'valiente',"ar":'شجاع',"fr":'courageux',"img":'brave',"cat":'emotions'},
    {"en":'run',"es":'correr',"ar":'يركض',"fr":'courir',"img":'running',"cat":'actions'},
    {"en":'jump',"es":'saltar',"ar":'يقفز',"fr":'sauter',"img":'jumping',"cat":'actions'},
    {"en":'walk',"es":'caminar',"ar":'يمشي',"fr":'marcher',"img":'walking',"cat":'actions'},
    {"en":'swim',"es":'nadar',"ar":'يسبح',"fr":'nager',"img":'swimming',"cat":'actions'},
    {"en":'fly',"es":'volar',"ar":'يطير',"fr":'voler',"img":'flying',"cat":'actions'},
    {"en":'eat',"es":'comer',"ar":'يأكل',"fr":'manger',"img":'eating',"cat":'actions'},
    {"en":'drink',"es":'beber',"ar":'يشرب',"fr":'boire',"img":'drinking',"cat":'actions'},
    {"en":'sleep',"es":'dormir',"ar":'ينام',"fr":'dormir',"img":'sleeping',"cat":'actions'},
    {"en":'read',"es":'leer',"ar":'يقرأ',"fr":'lire',"img":'reading',"cat":'actions'},
    {"en":'write',"es":'escribir',"ar":'يكتب',"fr":'écrire',"img":'writing',"cat":'actions'},
    {"en":'draw',"es":'dibujar',"ar":'يرسم',"fr":'dessiner',"img":'drawing',"cat":'actions'},
    {"en":'sing',"es":'cantar',"ar":'يغني',"fr":'chanter',"img":'singing',"cat":'actions'},
    {"en":'dance',"es":'bailar',"ar":'يرقص',"fr":'danser',"img":'dancing',"cat":'actions'},
    {"en":'play',"es":'jugar',"ar":'يلعب',"fr":'jouer',"img":'playing',"cat":'actions'},
    {"en":'laugh',"es":'reír',"ar":'يضحك',"fr":'rire',"img":'laughing',"cat":'actions'},
    {"en":'cry',"es":'llorar',"ar":'يبكي',"fr":'pleurer',"img":'crying',"cat":'actions'},
    {"en":'smile',"es":'sonreír',"ar":'يبتسم',"fr":'sourire',"img":'smiling',"cat":'actions'},
    {"en":'talk',"es":'hablar',"ar":'يتكلم',"fr":'parler',"img":'talking',"cat":'actions'},
    {"en":'help',"es":'ayudar',"ar":'يساعد',"fr":'aider',"img":'helping',"cat":'actions'},
    {"en":'cook',"es":'cocinar',"ar":'يطبخ',"fr":'cuisiner',"img":'cooking',"cat":'actions'},
    {"en":'big',"es":'grande',"ar":'كبير',"fr":'grand',"img":'big',"cat":'adjectives'},
    {"en":'small',"es":'pequeño',"ar":'صغير',"fr":'petit',"img":'small',"cat":'adjectives'},
    {"en":'tall',"es":'alto',"ar":'طويل',"fr":'grand/haut',"img":'tall',"cat":'adjectives'},
    {"en":'fast',"es":'rápido',"ar":'سريع',"fr":'rapide',"img":'fast',"cat":'adjectives'},
    {"en":'slow',"es":'lento',"ar":'بطيء',"fr":'lent',"img":'slow',"cat":'adjectives'},
    {"en":'hot',"es":'caliente',"ar":'ساخن',"fr":'chaud',"img":'hot',"cat":'adjectives'},
    {"en":'cold',"es":'frío',"ar":'بارد',"fr":'froid',"img":'cold',"cat":'adjectives'},
    {"en":'hard',"es":'duro',"ar":'صلب',"fr":'dur',"img":'hard',"cat":'adjectives'},
    {"en":'soft',"es":'suave',"ar":'ناعم',"fr":'doux',"img":'soft',"cat":'adjectives'},
    {"en":'clean',"es":'limpio',"ar":'نظيف',"fr":'propre',"img":'clean',"cat":'adjectives'},
    {"en":'dirty',"es":'sucio',"ar":'وسخ',"fr":'sale',"img":'dirty',"cat":'adjectives'},
    {"en":'heavy',"es":'pesado',"ar":'ثقيل',"fr":'lourd',"img":'heavy',"cat":'adjectives'},
    {"en":'light',"es":'ligero',"ar":'خفيف',"fr":'léger',"img":'light',"cat":'adjectives'},
    {"en":'new',"es":'nuevo',"ar":'جديد',"fr":'nouveau',"img":'new',"cat":'adjectives'},
    {"en":'old',"es":'viejo',"ar":'قديم',"fr":'vieux',"img":'old',"cat":'adjectives'},
    {"en":'beautiful',"es":'hermoso',"ar":'جميل',"fr":'beau',"img":'beautiful',"cat":'adjectives'},
    {"en":'strong',"es":'fuerte',"ar":'قوي',"fr":'fort',"img":'strong',"cat":'adjectives'},
    {"en":'sweet',"es":'dulce',"ar":'حلو',"fr":'sucré',"img":'sweet',"cat":'adjectives'},
    {"en":'sour',"es":'ácido',"ar":'حامض',"fr":'acide',"img":'sour',"cat":'adjectives'},
    {"en":'loud',"es":'ruidoso',"ar":'صاخب',"fr":'bruyant',"img":'loud',"cat":'adjectives'},
    {"en":'city',"es":'ciudad',"ar":'مدينة',"fr":'ville',"img":'city',"cat":'places'},
    {"en":'park',"es":'parque',"ar":'حديقة عامة',"fr":'parc',"img":'park',"cat":'places'},
    {"en":'market',"es":'mercado',"ar":'سوق',"fr":'marché',"img":'market',"cat":'places'},
    {"en":'hospital',"es":'hospital',"ar":'مستشفى',"fr":'hôpital',"img":'hospital',"cat":'places'},
    {"en":'restaurant',"es":'restaurante',"ar":'مطعم',"fr":'restaurant',"img":'restaurant',"cat":'places'},
    {"en":'bakery',"es":'panadería',"ar":'مخبزة',"fr":'boulangerie',"img":'bakery',"cat":'places'},
    {"en":'library',"es":'biblioteca',"ar":'مكتبة',"fr":'bibliothèque',"img":'library',"cat":'places'},
    {"en":'museum',"es":'museo',"ar":'متحف',"fr":'musée',"img":'museum',"cat":'places'},
    {"en":'zoo',"es":'zoo',"ar":'حديقة الحيوانات',"fr":'zoo',"img":'zoo',"cat":'places'},
    {"en":'cinema',"es":'cine',"ar":'سينما',"fr":'cinéma',"img":'cinema',"cat":'places'},
    {"en":'airport',"es":'aeropuerto',"ar":'مطار',"fr":'aéroport',"img":'airport',"cat":'places'},
    {"en":'playground',"es":'parque infantil',"ar":'ملعب',"fr":'aire de jeux',"img":'playground',"cat":'places'},
    {"en":'stadium',"es":'estadio',"ar":'ملعب رياضي',"fr":'stade',"img":'stadium',"cat":'places'},
    {"en":'mosque',"es":'mezquita',"ar":'مسجد',"fr":'mosquée',"img":'mosque',"cat":'places'},
    {"en":'farm',"es":'granja',"ar":'مزرعة',"fr":'ferme',"img":'farm',"cat":'places'},
    {"en":'castle',"es":'castillo',"ar":'قلعة',"fr":'château',"img":'castle',"cat":'places'},
    {"en":'bridge',"es":'puente',"ar":'جسر',"fr":'pont',"img":'bridge',"cat":'places'},
    {"en":'lighthouse',"es":'faro',"ar":'منارة',"fr":'phare',"img":'lighthouse',"cat":'places'},
    {"en":'fountain',"es":'fuente',"ar":'نافورة',"fr":'fontaine',"img":'fountain',"cat":'places'},
    {"en":'statue',"es":'estatua',"ar":'تمثال',"fr":'statue',"img":'statue',"cat":'places'},
]




# ═══════════════════ EMOJI MAP ═════════════════════════════════
WEMOJI={"apple":"🍎","banana":"🍌","orange":"🍊","strawberry":"🍓","grape":"🍇","mango":"🥭","watermelon":"🍉","pineapple":"🍍","cherry":"🍒","peach":"🍑","pear":"🍐","lemon":"🍋","coconut":"🥥","kiwi":"🥝","avocado":"🥑","blueberry":"🫐","pomegranate":"🍎","melon":"🍈","tangerine":"🍊","papaya":"🥭","lime":"🍋","fig":"🍈","date":"🌴","guava":"🍈","passion fruit":"🌺","carrot":"🥕","tomato":"🍅","potato":"🥔","onion":"🧅","cucumber":"🥒","pepper":"🌶️","spinach":"🥬","broccoli":"🥦","corn":"🌽","peas":"🫛","lettuce":"🥬","mushroom":"🍄","eggplant":"🍆","zucchini":"🥒","garlic":"🧄","pumpkin":"🎃","cabbage":"🥬","sweet potato":"🍠","cauliflower":"🥦","asparagus":"🌿","beetroot":"🫚","cat":"🐱","dog":"🐶","rabbit":"🐰","hamster":"🐹","parrot":"🦜","goldfish":"🐟","turtle":"🐢","horse":"🐴","cow":"🐄","sheep":"🐑","goat":"🐐","chicken":"🐔","duck":"🦆","donkey":"🫏","mouse":"🐭","guinea pig":"🐹","canary":"🐦","rooster":"🐓","lion":"🦁","tiger":"🐯","elephant":"🐘","giraffe":"🦒","zebra":"🦓","monkey":"🐒","gorilla":"🦍","bear":"🐻","wolf":"🐺","fox":"🦊","deer":"🦌","crocodile":"🐊","hippopotamus":"🦛","rhinoceros":"🦏","cheetah":"🐆","kangaroo":"🦘","koala":"🐨","panda":"🐼","polar bear":"🐻‍❄️","camel":"🐪","snake":"🐍","frog":"🐸","squirrel":"🐿️","hedgehog":"🦔","penguin":"🐧","dolphin":"🐬","whale":"🐳","shark":"🦈","octopus":"🐙","crab":"🦀","seahorse":"🐠","starfish":"⭐","jellyfish":"🪼","lobster":"🦞","clownfish":"🐠","seal":"🦭","eagle":"🦅","owl":"🦉","flamingo":"🦩","peacock":"🦚","toucan":"🦜","hummingbird":"🐦","sparrow":"🐦","swan":"🦢","butterfly":"🦋","bee":"🐝","ladybug":"🐞","ant":"🐜","bread":"🍞","rice":"🍚","pasta":"🍝","pizza":"🍕","soup":"🍜","egg":"🥚","cheese":"🧀","butter":"🧈","honey":"🍯","sandwich":"🥪","hamburger":"🍔","cake":"🎂","cookie":"🍪","ice cream":"🍦","chocolate":"🍫","chips":"🍟","popcorn":"🍿","candy":"🍬","jam":"🫙","yogurt":"🥛","pancake":"🥞","croissant":"🥐","donut":"🍩","salad":"🥗","meat":"🥩","waffle":"🧇","water":"💧","milk":"🥛","juice":"🍹","tea":"🍵","coffee":"☕","lemonade":"🍋","smoothie":"🥤","hot chocolate":"🍫","mint tea":"🍵","milkshake":"🥤","head":"💆","hair":"💇","eye":"👁️","ear":"👂","nose":"👃","mouth":"👄","tooth":"🦷","hand":"✋","finger":"☝️","arm":"💪","leg":"🦵","foot":"🦶","shoulder":"🤷","knee":"🦵","heart":"❤️","brain":"🧠","muscle":"💪","red":"🔴","blue":"🔵","yellow":"🟡","green":"🟢","orange":"🟠","purple":"🟣","pink":"🩷","black":"⚫","white":"⚪","brown":"🟤","grey":"🩶","shirt":"👔","t-shirt":"👕","dress":"👗","pants":"👖","jacket":"🧥","coat":"🧥","sweater":"🧶","shoes":"👟","boots":"👢","sneakers":"👟","sandals":"👡","socks":"🧦","hat":"🎩","cap":"🧢","scarf":"🧣","gloves":"🧤","pajamas":"🛌","swimsuit":"🩱","raincoat":"🌧️","house":"🏠","door":"🚪","window":"🪟","kitchen":"🍳","bedroom":"🛏️","bathroom":"🚿","living room":"🛋️","bed":"🛏️","chair":"🪑","table":"🍽️","sofa":"🛋️","lamp":"💡","fridge":"🧊","oven":"🔥","shower":"🚿","television":"📺","garden":"🌳","stairs":"🪜","school":"🏫","classroom":"🏫","teacher":"👩‍🏫","book":"📚","notebook":"📓","pencil":"✏️","pen":"🖊️","eraser":"⬜","ruler":"📏","scissors":"✂️","glue":"⬜","backpack":"🎒","board":"🖊️","calculator":"🔢","globe":"🌍","map":"🗺️","car":"🚗","bus":"🚌","train":"🚂","airplane":"✈️","boat":"⛵","bicycle":"🚲","motorcycle":"🏍️","truck":"🚛","ambulance":"🚑","helicopter":"🚁","taxi":"🚕","scooter":"🛴","rocket":"🚀","sun":"☀️","moon":"🌙","star":"⭐","cloud":"☁️","rain":"🌧️","snow":"❄️","rainbow":"🌈","tree":"🌳","flower":"🌸","river":"🌊","ocean":"🌊","mountain":"⛰️","desert":"🏜️","forest":"🌲","beach":"🏖️","lake":"🏞️","spring":"🌸","summer":"☀️","autumn":"🍂","winter":"❄️","wind":"💨","volcano":"🌋","island":"🏝️","waterfall":"🌊","mother":"👩","father":"👨","sister":"👧","brother":"👦","grandmother":"👵","grandfather":"👴","baby":"👶","girl":"👧","boy":"👦","friend":"🤝","doctor":"👨‍⚕️","nurse":"👩‍⚕️","police":"👮","firefighter":"👨‍🚒","chef":"👨‍🍳","farmer":"👨‍🌾","pilot":"👨‍✈️","astronaut":"👨‍🚀","football":"⚽","basketball":"🏀","tennis":"🎾","swimming":"🏊","cycling":"🚴","running":"🏃","gymnastics":"🤸","skiing":"⛷️","surfing":"🏄","boxing":"🥊","chess":"♟️","puzzle":"🧩","kite":"🪁","trampoline":"🤸","bowling":"🎳","ping pong":"🏓","happy":"😊","sad":"😢","angry":"😠","scared":"😨","surprised":"😲","excited":"🤩","tired":"😴","hungry":"🤤","thirsty":"💧","bored":"😑","proud":"💪","shy":"😳","calm":"😌","love":"❤️","brave":"💪","run":"🏃","jump":"⬆️","walk":"🚶","swim":"🏊","fly":"✈️","eat":"🍽️","drink":"🥤","sleep":"😴","read":"📖","write":"✍️","draw":"🎨","sing":"🎤","dance":"💃","play":"🎮","laugh":"😂","cry":"😭","smile":"😊","talk":"💬","help":"🤝","cook":"👨‍🍳","big":"🐘","small":"🐭","tall":"🦒","fast":"🏎️","slow":"🐢","hot":"🔥","cold":"❄️","hard":"🪨","soft":"🛌","clean":"✨","dirty":"🗑️","heavy":"⚖️","light":"🪶","new":"✨","old":"📜","beautiful":"🌸","strong":"💪","sweet":"🍬","sour":"🍋","loud":"📢","city":"🏙️","park":"🌳","market":"🛒","hospital":"🏥","restaurant":"🍽️","bakery":"🥖","library":"📚","museum":"🏛️","zoo":"🦁","cinema":"🎬","airport":"✈️","playground":"🎠","stadium":"🏟️","mosque":"🕌","farm":"🚜","castle":"🏰","bridge":"🌉","lighthouse":"🗼","fountain":"⛲","statue":"🗽"}
CEMOJI={"fruits":"🍎","vegetables":"🥕","animals":"🐱","wild_animals":"🦁","sea":"🐬","birds":"🦜","insects":"🦋","food":"🍕","drinks":"🥤","body":"💪","colors":"🎨","clothes":"👕","home":"🏠","school":"📚","transport":"🚗","nature":"🌿","family":"👨‍👩‍👧","sports":"⚽","emotions":"😊","actions":"🏃","adjectives":"✨","places":"🏙️"}
LANGBG={"english":(29,78,216),"spanish":(185,28,28),"arabic":(157,23,77)}

# ═══════════════════ CURRICULUM 200 THÈMES ═══════════════════════
MATH=["Compter jusqu'à 20","Additions jusqu'à 10","Soustractions jusqu'à 10","Additions et soustractions mélangées","Compter jusqu'à 50","Les formes géométriques","Additions jusqu'à 15","Soustractions jusqu'à 15","Plus grand plus petit égal","Les dizaines 10-50","Additions jusqu'à 20","Soustractions jusqu'à 20","Compter jusqu'à 100","Nombres pairs et impairs","Additions avec retenue","Compter de 2 en 2 et 5 en 5","Mesures long court lourd léger","Heure heures entières","Les doubles 2+2 3+3","Décomposer un nombre","Additions à 3 termes","Soustractions avec emprunt","Fractions 1/2 visuelles","Ordonner les nombres","Argent pièces de monnaie","Groupes de 10","Additions jusqu'à 30","Soustractions jusqu'à 30","Patterns numériques","Compléter à 10","Solides cube sphère cylindre","Additions jusqu'à 50","Soustractions jusqu'à 50","Heure demi-heures","Calendrier et dates","Problème addition contexte","Problème soustraction","Fractions 1/3 et 1/4","Trouver le nombre manquant","Additions jusqu'à 100","Soustractions jusqu'à 100","Périmètre forme simple","Problème mixte","Billets de banque","Suites numériques","Heure quart d'heure","Additions 2 chiffres sans retenue","Soustractions 2 chiffres","Combien reste-t-il","Combien en tout","Additions 2 chiffres avec retenue","Soustractions emprunt avancé","Multiplication addition répétée","Table x2","Table x5","Table x10","Problème multiplication","Calcul mental additions","Calcul mental soustractions","Fractions d'une quantité","Table x3","Lire une montre","Rendre la monnaie","Additions 3 chiffres","Soustractions 3 chiffres","Table x4","Comparer fractions","Mesures cm et m","Problème 2 étapes","Table x6","Centaines 100-1000","Mesures g et kg","Table x7","Partage égal","Fractions 2/3 et 3/4","Nombres jusqu'à 1000","Table x8","Durées simples","Mesures litres","Table x9","Tables mélangées 2-5","Périmètre formule","Aire carreaux","Problème mult","Tables mélangées 2-9","Division partage","Division groupement","Problème division","Fractions droite numérique","Tables chrono","Aire L fois l","Nombres 10000","Addition 4 chiffres","Problème complexe","Révision multi","Divisions 2-5","Divisions 6-9","Fractions numérateur manquant","Fractions équivalentes","Fractions collection","Mult 2x1","Angles","Aire périmètre","Décimaux intro","Vitesse simple","Division reste","Fractions même dénominateur","Mult 2x2","Symétrie","Prix monnaie","Division dividende","Conversion mesures","Recette fract","Mult 100 1000","Cercle diamètre","Décimaux dixièmes","Réduction pourcent","Fractions add diff dénominator","Mult 3x1","Division longue","Probabilité","Graphiques","Angle triangle","Fractions soustraction","Nombres négatifs","Voyage distance","Puissances 10","Estimation","Polygones","VDT","Suites complexes","Fractions mult","Coordonnées","Volume","4 opérations","Comparaison prix","Division avancée","Fractions div","Algèbre","Équations","Pythagore","Fractions avancées","Pourcentages","Augmentation réduction","Statistiques","Transformations","Nombres premiers","Budget pourcent","Carrés cubes","Probabilité calcul","Règle 3","Aire triangle","Graphique tendance","Fractions décimaux","Aire cercle","Combinatoire","Probabilité sim","Division euclidienne","Système équations","Chronogramme","Optimisation","Olympique 1","Olympique 2","Olympique 3","Problème ouvert","Révision 1","Révision 2","Mini concours","Concours 6ème","JOUR 200"]
LOGIC=["Suite formes","Intrus liste","Motif miroir","Labyrinthe","Classer animaux","Suites couleurs","Association","Taille ordre","Manque image","Analogie","Suite 1,3,5,7","Vrai Faux","Classer catégorie","Différences","Sudoku images","Qui suis-je","Chronologie","Orientation","Intrus numérique","Code A=1","Balance","Alphabétique","Partage","Ombres","Syllogisme","Allumettes","Suites images","Si alors","Mots fléchés","Tangram","Triangles cachés","Menteur vrai","Ordre histoire","Poids","Lettres A,C,E","3 chapeaux","Carte NSEO","Cubes 3D","Tableau 3x3","Ressemblances","Cryptarithmie","Relier points","Grenouille","Morpion","Vitesse arrivée","Berger","Colorier code","Mot envers","Ages indices","Devinette géo","Sudoku 4x4","Analogies visuelles","Calendrier","Transvaser","Fibonacci","Cryptarithmie 2","Kim","Escaliers","Hanoï","Probabilité billes","Picross","Déduction chaine","Classement","Alternées","3 maisons","Pyramide","Balance poids","Décoder grille","Matrices 3x3","Suites géo","Vérité mensonge","Doigts 1000","Ages complexe","Faces peintes","Grille 4x4","Analogie abstraite","Vue 3D","Voyage temps","Mots croisés","Binaire","Venn","Partage inégal","Côtés suites","Hamiltonien","Heure arrivée","Grenouilles 7","Carrés suite","21 bâtonnets","Cavaliers","Conway","Possible certain","Trains","5 suspects","Pascal","Poignées mains","Nonogramme","Carré magique 3","Fractal","Balance 12","César","Ensembles","Nim","Contradiction","Monnaie façons","Eulérien","Fibonacci variant","N reines","Carré magique 4","Voyageur","Chevaliers","Paradoxe","Floue","8 reines","Épistémique","100 prisonniers","Premiers","Sac à dos","Latin 5x5","Zénon","Minimax","Huffman","Dominos","Tri bulles","Coloration","Induction","Temporel","Koch","Invente suite","Zebra","Révision","Sans calculer","Socrate","Méta-logique","JOUR 200"]


# ═══════════════════ ARABE : PHONÉTIQUE ══════════════════════════
PHON={
"تفاحة":"tuf-fā-ḥa","موزة":"maw-za","برتقالة":"bur-tu-qā-la","فراولة":"fa-rā-wi-la",
"عنب":"'i-nab","مانجو":"man-jū","بطيخ":"bat-tīkh","أناناس":"a-nā-nās","كرز":"ka-raz",
"خوخ":"khawkh","كمثرى":"kum-mith-rā","ليمون":"lay-mūn","جوز الهند":"jawz al-hind",
"كيوي":"kī-wī","أفوكادو":"a-fū-kā-dū","رمان":"rum-mān","شمام":"sham-mām",
"يوسفي":"yū-su-fī","بابايا":"bā-bā-yā","تمر":"ta-mar","جوافة":"ja-wā-fa",
"جزرة":"ja-za-ra","طماطم":"ta-mā-tim","بطاطا":"ba-tā-ta","بصلة":"ba-ṣa-la",
"خيار":"khi-yār","فلفل":"ful-ful","سبانخ":"sa-bā-nikh","بروكلي":"bruk-lī",
"ذرة":"dhu-ra","كرنب":"kar-nab","بطاطا حلوة":"ba-ṭā-ṭā ḥul-wa","قرنبيط":"qar-na-bīṭ",
"هليون":"hal-yūn","شمندر":"sha-man-dar","قطة":"qit-ta","كلب":"kalb","أرنب":"ar-nab",
"هامستر":"ham-ster","ببغاء":"bab-ba-ghā'","سلحفاة":"sul-ḥa-fā","حصان":"ḥi-ṣān",
"بقرة":"ba-qa-ra","خروف":"kha-rūf","ماعز":"mā-'iz","دجاجة":"da-jā-ja","بطة":"bat-ta",
"حمار":"ḥi-mār","فأر":"fa'r","كناري":"ka-nā-rī","ديك":"dīk","أسد":"a-sad",
"نمر":"na-mir","فيل":"fīl","زرافة":"za-rā-fa","حمار وحشي":"ḥi-mār wah-shī",
"قرد":"qird","غوريلا":"ghū-rīl-lā","دب":"dubb","ذئب":"dhi'b","ثعلب":"tha'-lab",
"غزال":"gha-zāl","تمساح":"tim-sāḥ","فرس البحر":"fa-ras al-baḥr",
"وحيد القرن":"wa-ḥīd al-qarn","فهد":"fahd","كنغر":"kan-ghur","كوالا":"kū-wā-lā",
"باندا":"bān-dā","دب قطبي":"dubb qu-ṭbī","جمل":"ja-mal","ثعبان":"thu'-bān",
"ضفدع":"ḍif-da'","سنجاب":"sun-jāb","قنفذ":"qun-fudh","بطريق":"bat-rīq",
"دلفين":"dul-fīn","حوت":"ḥūt","قرش":"qirsh","أخطبوط":"ukh-tu-būt",
"سرطان البحر":"sar-ṭān al-baḥr","أبو رمال":"a-bū rum-māl",
"نجم البحر":"najm al-baḥr","قنديل البحر":"qun-dīl al-baḥr",
"كركند":"kar-kand","سمكة مهرج":"sa-ma-kat mu-har-rij","فقمة":"fiq-ma",
"نسر":"na-sar","بوم":"būm","نحام":"na-ḥām","طاووس":"ṭā-wūs",
"طوقان":"ṭū-qān","طائر طنان":"ṭā'ir ta-nnān","عصفور":"'us-fūr","بجعة":"ba-ja-'a",
"فراشة":"fa-rā-sha","نحلة":"naḥ-la","دعسوقة":"du'-sū-qa","نملة":"nam-la",
"خبز":"khubz","أرز":"a-ruzz","مكرونة":"ma-ka-rū-na","بيتزا":"bī-tzā",
"شوربة":"shu-ra-ba","بيضة":"bay-ḍa","جبن":"jubn","زبدة":"zub-da","عسل":"'a-sal",
"ساندويتش":"sand-wīsh","همبرغر":"hum-bur-ghar","كعكة":"ka'-ka","كوكيز":"kū-kīz",
"آيس كريم":"'āys krīm","شوكولاتة":"shu-ku-lā-ta","رقائق":"ra-qā'iq","فشار":"fi-shār",
"حلوى":"ḥal-wā","مربى":"mu-rab-bā","زبادي":"za-bā-dī","فطيرة":"fa-ṭī-ra",
"كرواسان":"krū-wā-sān","دونات":"dū-nāt","سلطة":"sal-ṭa","لحم":"laḥm","وافل":"wā-fil",
"ماء":"mā'","حليب":"ḥa-līb","عصير":"'a-ṣīr","شاي":"shāy","قهوة":"qah-wa",
"ليمونادة":"lay-mu-nā-da","شوكولاتة ساخنة":"shu-ku-lā-ta sā-khi-na",
"شاي بالنعناع":"shāy bil-na'-nā'","ميلك شيك":"mīlk shīk",
"رأس":"ra's","شعر":"sha'r","عين":"'ayn","أذن":"u-dhun","أنف":"anf","فم":"famm",
"سن":"sinn","يد":"yad","إصبع":"iṣ-ba'","ذراع":"dhirā'","ساق":"sāq","قدم":"qa-dam",
"كتف":"ka-tif","ركبة":"rak-ba","قلب":"qalb","مخ":"mukhkh","عضلة":"'a-ḍa-la",
"أحمر":"aḥ-mar","أزرق":"az-raq","أصفر":"aṣ-far","أخضر":"akh-ḍar",
"برتقالي":"bur-tu-qā-lī","بنفسجي":"bun-fus-jī","وردي":"war-dī",
"أسود":"as-wad","أبيض":"ab-yaḍ","بني":"bun-nī","رمادي":"ra-mā-dī",
"قميص":"qa-mīṣ","فستان":"fus-tān","بنطلون":"ban-ṭa-lūn","جاكيت":"jā-kit",
"معطف":"mi'-ṭaf","بلوزة":"bu-lū-za","أحذية":"aḥ-dhi-ya","حذاء بوت":"ḥi-dhā' būt",
"حذاء رياضي":"ḥi-dhā' ri-yā-ḍī","صندل":"ṣan-dal","جوارب":"jaw-wā-rib",
"قبعة":"qub-ba'a","طاقية":"ṭā-qi-ya","وشاح":"wi-shāḥ","قفازات":"qi-fā-zāt",
"بيجاما":"bī-jā-mā","ملابس سباحة":"ma-lā-bis si-bā-ḥa","معطف مطر":"mi'-ṭaf ma-ṭar",
"بيت":"bayt","باب":"bāb","نافذة":"nā-fi-dha","مطبخ":"maṭ-bakh",
"غرفة نوم":"ghur-fat nawm","حمام":"ḥam-mām","غرفة معيشة":"ghur-fat ma-'ī-sha",
"سرير":"sa-rīr","كرسي":"kur-sī","طاولة":"ṭā-wi-la","أريكة":"a-rī-ka",
"مصباح":"miṣ-bāḥ","ثلاجة":"tal-lā-ja","فرن":"furn","دش":"dush",
"تلفاز":"til-fāz","حديقة":"ḥa-dī-qa","سلم":"sul-lam",
"مدرسة":"mad-ra-sa","فصل دراسي":"faṣl di-rā-sī","معلم":"mu-'al-lim",
"كتاب":"ki-tāb","دفتر":"daf-tar","قلم رصاص":"qa-lam ra-ṣāṣ","قلم":"qa-lam",
"ممحاة":"mim-ḥā","مسطرة":"mis-ṭa-ra","مقص":"miq-aṣṣ","غراء":"ghi-rā'",
"حقيبة مدرسية":"ḥa-qī-bat mad-ra-si-ya","سبورة":"sab-bū-ra",
"آلة حاسبة":"ā-lat ḥā-si-ba","كرة الأرض":"ku-rat al-arḍ","خريطة":"kha-rī-ṭa",
"سيارة":"say-yā-ra","حافلة":"ḥā-fi-la","قطار":"qi-ṭār","طائرة":"ṭā'i-ra",
"قارب":"qā-rib","دراجة":"dar-rā-ja","دراجة نارية":"dar-rā-ja nā-ri-ya",
"شاحنة":"shā-ḥi-na","سيارة إسعاف":"say-yā-rat is-'āf",
"طائرة مروحية":"ṭā'i-ra mir-waḥī-ya","تاكسي":"tāk-sī","سكوتر":"skū-tar",
"صاروخ":"ṣā-rūkh","شمس":"shams","قمر":"qa-mar","نجمة":"naj-ma",
"سحابة":"sa-ḥā-ba","مطر":"ma-ṭar","ثلج":"thalj","قوس قزح":"qaws qa-zaḥ",
"شجرة":"sha-ja-ra","زهرة":"zah-ra","نهر":"na-har","محيط":"mu-ḥīṭ","جبل":"ja-bal",
"صحراء":"ṣaḥ-rā'","غابة":"ghā-ba","شاطئ":"shā-ṭi'","بحيرة":"bu-ḥay-ra",
"ربيع":"ra-bī'","صيف":"ṣayf","خريف":"kha-rīf","شتاء":"shi-tā'","ريح":"rīḥ",
"بركان":"bur-kān","جزيرة":"ja-zī-ra","شلال":"shal-lāl","أم":"umm","أب":"ab",
"أخت":"ukht","أخ":"akh","جدة":"jad-da","جد":"jadd","رضيع":"ra-ḍī'",
"بنت":"bint","ولد":"wa-lad","صديق":"ṣa-dīq","طبيب":"ṭa-bīb",
"ممرضة":"mu-mar-riḍa","شرطي":"shur-ṭī","إطفائي":"iṭ-fā'ī","طاهٍ":"ṭā-hin",
"مزارع":"muz-zā-ri'","طيار":"ṭay-yār","رائد فضاء":"rā'id fa-ḍā'",
"كرة القدم":"ku-rat al-qa-dam","كرة السلة":"ku-rat as-sal-la","تنس":"ti-nis",
"سباحة":"si-bā-ḥa","ركوب الدراجة":"ru-kūb ad-dar-rā-ja","الجري":"al-ja-rī",
"جمباز":"jam-bāz","تزلج":"ta-zal-luj","ركوب الأمواج":"ru-kūb al-am-wāj",
"ملاكمة":"mu-lā-ka-ma","شطرنج":"sha-ṭa-ranj","أحجية":"uh-jī-ya",
"طائرة ورقية":"ṭā'i-ra wa-ra-qi-ya","ترامبولين":"trām-bū-līn",
"بولينغ":"bū-līng","تنس طاولة":"ti-nis ṭā-wi-la","سعيد":"sa-'īd",
"حزين":"ḥa-zīn","غاضب":"ghā-ḍib","خائف":"khā'if","مندهش":"mun-da-hish",
"متحمس":"mu-ta-ḥam-mis","متعب":"mu-ta-'ab","جائع":"jā-'i'","عطشان":"'aṭ-shān",
"ممل":"mu-mil","فخور":"fa-khūr","خجول":"kha-jūl","هادئ":"hā-di'","حب":"ḥubb",
"شجاع":"shujā'","يركض":"yar-kuḍ","يقفز":"yaq-fiz","يمشي":"yam-shī",
"يسبح":"yas-baḥ","يطير":"ya-ṭīr","يأكل":"ya'-kul","يشرب":"yash-rab",
"ينام":"ya-nām","يقرأ":"yaq-ra'","يكتب":"yak-tub","يرسم":"yar-sum",
"يغني":"yugh-annī","يرقص":"yar-quṣ","يلعب":"yal-'ab","يضحك":"yaḍ-ḥak",
"يبكي":"yab-kī","يبتسم":"yab-ta-sim","يتكلم":"ya-ta-kal-lam","يساعد":"yu-sā-'id",
"يطبخ":"yaṭ-bukh","كبير":"ka-bīr","صغير":"ṣa-ghīr","طويل":"ṭa-wīl",
"سريع":"sa-rī'","بطيء":"ba-ṭī'","ساخن":"sā-khun","بارد":"bā-rid","صلب":"ṣulb",
"ناعم":"nā-'im","نظيف":"na-ẓīf","وسخ":"wa-sikh","ثقيل":"tha-qīl","خفيف":"kha-fīf",
"جديد":"ja-dīd","قديم":"qa-dīm","جميل":"ja-mīl","قوي":"qa-wī","حلو":"ḥu-lw",
"حامض":"ḥā-miḍ","صاخب":"ṣā-khib","مدينة":"ma-dī-na",
"حديقة عامة":"ḥa-dī-qa 'āmma","سوق":"sūq","مستشفى":"mus-tash-fā",
"مطعم":"maṭ-'am","مخبزة":"makh-ba-za","مكتبة":"mak-ta-ba","متحف":"mat-ḥaf",
"حديقة الحيوانات":"ḥa-dī-qat al-ḥay-wa-nāt","سينما":"sī-na-mā",
"مطار":"ma-ṭār","ملعب":"mal-'ab","ملعب رياضي":"mal-'ab ri-yā-ḍī",
"مسجد":"mas-jid","مزرعة":"maz-ra-'a","قلعة":"qal-'a","جسر":"jisr",
"منارة":"ma-nā-ra","نافورة":"nā-fū-ra","تمثال":"tim-thāl",
}

# Progression alphabet arabe
ARALPHA={
1:[("ا","alif","a"),("ب","ba","b"),("ت","ta","t"),("ث","tha","th"),("ج","jim","j")],
2:[("ح","ha","ḥ"),("خ","kha","kh"),("د","dal","d"),("ذ","dhal","dh"),("ر","ra","r")],
3:[("ز","zayn","z"),("س","sin","s"),("ش","shin","sh"),("ص","sad","ṣ"),("ض","dad","ḍ")],
4:[("ط","ta","ṭ"),("ظ","dha","ẓ"),("ع","'ayn","'"),("غ","ghayn","gh"),("ف","fa","f")],
5:[("ق","qaf","q"),("ك","kaf","k"),("ل","lam","l"),("م","mim","m"),("ن","nun","n")],
6:[("ه","ha","h"),("و","waw","w/ū"),("ي","ya","y/ī"),("ة","ta marbuta","a"),("ء","hamza","'")],
}


# ═══════════════════ SCHEDULE + IMAGES ══════════════════════════
_SCH = None

def _build():
    n=len(WORDS); rng=random.Random(2026); slots=[]
    for _ in range(4):
        r=list(range(n)); rng.shuffle(r); slots.extend(r)
    rng.shuffle(slots); sch={}; ls={}
    for day in range(1,201):
        ch,buf,seen=[],[],set()
        for i in slots:
            if i in seen: continue
            if day-ls.get(i,0)>=10: ch.append(i); seen.add(i)
            else: buf.append(i)
            if len(ch)==10: break
        for i in buf:
            if i not in seen: ch.append(i); seen.add(i)
            if len(ch)==10: break
        for i in ch: ls[i]=day
        sch[str(day)]={}
        for lg,k in[("english","en"),("spanish","es"),("arabic","ar")]:
            sch[str(day)][lg]=[{"word":WORDS[i][k],"word_en":WORDS[i]["en"],"french":WORDS[i]["fr"],"img":WORDS[i]["img"],"cat":WORDS[i]["cat"],"id":i} for i in ch]
    return sch

def sched():
    global _SCH; _SCH=_SCH or _build(); return _SCH

def wday(d): return sched().get(str(d),{})

def tday():
    d=(date.today()-START_DATE).days+1
    return d if 1<=d<=200 else None

def _make_img(en,disp,fr,cat,lang,sz=200):
    em=WEMOJI.get(en.lower()) or CEMOJI.get(cat,"📌")
    bg=LANGBG.get(lang,(79,70,229)); dk=tuple(max(0,v-60) for v in bg)
    img=PI.new("RGBA",(sz,sz),(*bg,255)); draw=ImageDraw.Draw(img)
    for y in range(sz):
        t=y/sz; c=tuple(int(dk[i]*(1-t)+bg[i]*t) for i in range(3))
        draw.line([(0,y),(sz,y)],fill=(*c,255))
    ph=sz*9//25
    draw.ellipse([(-50,sz-ph-30),(sz+50,sz-ph+30)],fill=(255,255,255,255))
    draw.rectangle([(0,sz-ph),(sz,sz)],fill=(255,255,255,255))
    cy=(sz-ph)//2; cr=(sz-ph)//2-12
    draw.ellipse([(sz//2-cr,cy-cr),(sz//2+cr,cy+cr)],fill=(255,255,255,60))
    if Path(_EMOJ).exists():
        for es in [109,72,36]:
            try:
                ef=ImageFont.truetype(_EMOJ,es)
                draw.text((sz//2-es//2,cy-es//2),em,font=ef,embedded_color=True); break
            except: continue
    else:
        ff=_fnt(_BOLD,44); draw.text((sz//2,cy),em,fill=(255,255,255,200),font=ff,anchor="mm")
    draw.line([(16,sz-ph+7),(sz-16,sz-ph+7)],fill=(*bg,150),width=2)
    wf=_fnt(_BOLD,20); wd=disp.upper() if len(disp)<=13 else disp.upper()[:11]+"…"
    draw.text((sz//2,sz-ph+18),wd,fill=(*bg,255),font=wf,anchor="mt")
    draw.line([(16,sz-28),(sz-16,sz-28)],fill=(215,215,215,255),width=1)
    sf=_fnt(_REG,11); fd=fr if len(fr)<=22 else fr[:20]+"…"
    draw.text((sz//2,sz-13),fd,fill=(85,85,85,255),font=sf,anchor="mb")
    rgb=PI.new("RGB",(sz,sz),(255,255,255)); rgb.paste(img,mask=img.split()[3])
    buf=io.BytesIO(); rgb.save(buf,"JPEG",quality=80,optimize=True); return buf.getvalue()

def _pb(q):
    if not PIXABAY_KEY: return None
    try:
        r=_req.get("https://pixabay.com/api/",params={"key":PIXABAY_KEY,"q":q,"image_type":"photo","per_page":3,"safesearch":"true"},timeout=8)
        h=r.json().get("hits",[])
        if h:
            d=_req.get(h[0].get("previewURL",""),timeout=8).content
            if len(d)>2000: return d
    except: pass

def _pp(q):
    if not PEXELS_KEY: return None
    try:
        r=_req.get("https://api.pexels.com/v1/search",params={"query":q,"per_page":1,"size":"small"},headers={"Authorization":PEXELS_KEY},timeout=8)
        p=r.json().get("photos",[])
        if p:
            u=p[0]["src"].get("tiny","")
            if u:
                d=_req.get(u,timeout=8).content
                if len(d)>2000: return d
    except: pass

def _pw(q):
    try:
        r=_req.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{q.replace(' ','_').title()}",timeout=8)
        if r.ok:
            u=r.json().get("thumbnail",{}).get("source","")
            if u:
                d=_req.get(u,timeout=8).content
                if len(d)>2000: return d
    except: pass

def gimg(en,disp,fr,cat,lang,sz=200):
    k=f"{lang}_{en.lower().replace(' ','_')}"; cf=IMG_CACHE/f"{k}.jpg"
    if cf.exists(): return io.BytesIO(cf.read_bytes())
    raw=_pb(en) or _pp(en) or _pw(en) or _make_img(en,disp,fr,cat,lang,sz)
    cf.write_bytes(raw); return io.BytesIO(raw)


MATH.extend(["Compter jusqu'à 200","Compter jusqu'à 500","Compter jusqu'à 1000","Nombres romains I à X","Suites par bonds de 3","Problème monnaie complex","Vitesse et temps","Mesures température","Angles complémentaires supplémentaires","Fractions improper","Nombres décimaux additions","Nombres décimaux soustractions","Probabilité événements simples","Aire trapèze","Théorème Pythagore applications","Nombres négatifs opérations","Moyennes pondérées","Conversion fractions décimaux pourcent","Puissances entières","Racines carrées simples","Factorisation premiers","PGCD et PPCM","Équations 2 degrés simples","Paraboles et graphiques","JOUR 200 Grand défi final","Révision intégrale complète","Problème de vitesse train","Problème de mélange proportionnel","Défi international adapté","Applications vie quotidienne"])
while len(MATH) < 200: MATH.append(f"Défi mathématiques niveau {len(MATH)+1}")
MATH = MATH[:200]

LOGIC.extend(["Suite de Collatz","Problème des 4 couleurs","Tours de Hanoï 4 disques","Cryptographie simple","Suites récursives avancées","Logique modale avancée","Paradoxe du barbier","Problème salaire logique","Automate fini simple","Démonstration par récurrence","Logique des prédicats","Problème des ponts Königsberg","Invariant dans un problème","Raisonnement par l'absurde","Problème de la cigale fourmi","Suites de nombres premiers","Suite logistique","Problème du sac de billets","Topologie discrète intro","Graphe bipartite","Algorithme de tri insertion","Complexité algorithmique","Problème du rendez-vous","Logique épistémique avancée","JOUR 200 Défi ultime","Révision finale complète","Enigme du prisonnier","Paradoxe de Simpson","Problème de décision","Jeu de Nim généralisé"])
while len(LOGIC) < 200: LOGIC.append(f"Défi logique niveau {len(LOGIC)+1}")
LOGIC = LOGIC[:200]

# ═══════════════════ PDF HELPERS ════════════════════════════════
def _b(h): return colors.HexColor(h)
def _pn(n,**k): return ParagraphStyle(n,**k)
def _bn(em,ti,su,dk,mn):
    d=[[Paragraph(f"{em}  <b>{ti}</b>",_pn("bt",fontName="Helvetica-Bold",fontSize=16,textColor=colors.white,leading=20)),
        Paragraph(su,_pn("bs",fontName="Helvetica-Oblique",fontSize=10,textColor=_b("#e5e7eb"),leading=13))]]
    t=Table(d,colWidths=[9*cm,CW-9*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),dk),("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROUNDEDCORNERS",[8])]))
    return t
def _al(lb=""):
    d=[[Paragraph(f"<i>{lb}</i>",_pn("sm",fontName="Helvetica",fontSize=9,textColor=_b("#6b7280"),leading=12)),
        Paragraph("_"*50,_pn("al",fontName="Helvetica",fontSize=11,textColor=_b("#d1d5db"),leading=16))]]
    t=Table(d,colWidths=[3.5*cm,CW-3.5*cm])
    t.setStyle(TableStyle([("BOTTOMPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),2),("LEFTPADDING",(0,0),(-1,-1),0)]))
    return t
def _st(lb):
    d=[[lb,"☆  ☆  ☆  ☆  ☆"]]
    t=Table(d,colWidths=[11*cm,CW-11*cm])
    t.setStyle(TableStyle([("FONTNAME",(0,0),(0,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(0,0),11),
        ("FONTNAME",(1,0),(1,0),"Helvetica"),("FONTSIZE",(1,0),(1,0),20),
        ("TEXTCOLOR",(1,0),(1,0),_b("#f59e0b")),("TOPPADDING",(0,0),(-1,-1),8)]))
    return t
def _pe(html,n):
    if not html: return [f"Exercice {i}" for i in range(1,n+1)]
    t=re.sub(r"<[^>]+"," ",html); t=re.sub(r"&[a-z]+;"," ",t); t=re.sub(r"\s+"," ",t).strip()
    p=re.split(r"\b[1-9][0-9]?\.\s+",t)
    p=[x.strip()[:280] for x in p if len(x.strip())>15]
    if len(p)>=n: return p[:n]
    c=max(len(t)//n,40); return [(t[i*c:(i+1)*c].strip() or f"Ex {i+1}") for i in range(n)]

LCFG={
    "english":("🇬🇧","ANGLAIS · English","Répète chaque mot 3× à voix haute !",_b("#1e3a8a"),_b("#2563eb"),_b("#dbeafe")),
    "spanish":("🇪🇸","ESPAGNOL · Español","Répète chaque mot 3× !",_b("#7f1d1d"),_b("#dc2626"),_b("#fee2e2")),
}

def _cov(cv,day,today,pct,words):
    cv.setFillColor(_b("#3730a3")); cv.rect(0,0,W,H,fill=1,stroke=0)
    cv.setFillColor(_b("#6d28d9")); cv.circle(W*.88,H*.90,72,fill=1,stroke=0)
    cv.setFillColor(_b("#4c1d95")); cv.circle(W*.1,H*.87,46,fill=1,stroke=0)
    cv.setFont("Helvetica-Bold",36); cv.setFillColor(colors.white)
    cv.drawCentredString(W/2,H*.80,"🎓  Professeur du Jour")
    cv.setFont("Helvetica",16); cv.setFillColor(_b("#c4b5fd"))
    cv.drawCentredString(W/2,H*.74,f"Jour {day}/200  ·  {today}")
    px,py,pw,ph=1.5*cm,H*.22,W-3*cm,H*.49
    cv.setFillColor(colors.white); cv.roundRect(px,py,pw,ph,15,fill=1,stroke=0)
    cv.setFillColor(_b("#3730a3")); cv.setFont("Helvetica-Bold",13)
    cv.drawString(px+.8*cm,py+ph-1.2*cm,f"📊  Progression : {pct}%  ({day}/200)")
    bx,by,bw,bh=px+.8*cm,py+ph-2.1*cm,pw-1.6*cm,.55*cm
    cv.setFillColor(_b("#e5e7eb")); cv.roundRect(bx,by,bw,bh,5,fill=1,stroke=0)
    cv.setFillColor(_b("#6d28d9")); cv.roundRect(bx,by,max(bw*(pct/100),5),bh,5,fill=1,stroke=0)
    cv.setFillColor(_b("#3730a3")); cv.setFont("Helvetica-Bold",13)
    cv.drawString(px+.8*cm,py+ph-3.2*cm,"📋  Programme · 1h30 :")
    subs=[("⭐","Maths","20min",_b("#2563eb")),("🧠","Logique","15min",_b("#16a34a")),
          ("🇬🇧","Anglais","20min",_b("#3b82f6")),("🇪🇸","Espagnol","20min",_b("#ef4444")),
          ("🌙","Arabe","15min",_b("#db2777"))]
    sw=(pw-1.6*cm)/5
    for i,(em,nm,dr,cl) in enumerate(subs):
        bx2=px+.8*cm+i*sw; by2=py+ph-4.6*cm
        cv.setFillColor(cl); cv.roundRect(bx2,by2,sw-5,1.2*cm,8,fill=1,stroke=0)
        cv.setFillColor(colors.white); cv.setFont("Helvetica-Bold",14)
        cv.drawCentredString(bx2+sw/2-3,by2+.6*cm,em)
        cv.setFont("Helvetica",8); cv.drawCentredString(bx2+sw/2-3,by2+.15*cm,dr)
    cv.setFillColor(_b("#3730a3")); cv.setFont("Helvetica-Bold",12)
    cv.drawString(px+.8*cm,py+ph-5.8*cm,"🔤  Les 10 mots du jour par langue :")
    for li,(fl,wds,cl) in enumerate([("🇬🇧",words.get("english",[]),_b("#2563eb")),
                                      ("🇪🇸",words.get("spanish",[]),_b("#ef4444")),
                                      ("🌙",words.get("arabic",[]),_b("#db2777"))]):
        ry=py+ph-6.6*cm-li*.72*cm
        cv.setFillColor(cl); cv.setFont("Helvetica-Bold",11); cv.drawString(px+.8*cm,ry,f"{fl}  ")
        cv.setFillColor(_b("#374151")); cv.setFont("Helvetica",10)
        pr="  ·  ".join(w["word"] for w in wds[:7])+((" ···") if len(wds)>7 else "")
        cv.drawString(px+2.1*cm,ry,pr)

def _vsec(lang,words):
    fl,ti,tp,d,m,l=LCFG[lang]; story=[_bn(fl,ti,tp,d,m),Spacer(1,.4*cm)]
    cw,ch=8.2*cm,7.5*cm; ih=ch-3.2*cm
    for i in range(0,len(words),2):
        row=[]
        for j in range(2):
            if i+j>=len(words): row.append(Spacer(cw,ch)); continue
            w=words[i+j]
            ib=gimg(w["word_en"],w["word"],w["french"],w["cat"],lang,200)
            inn=[]
            try: inn.append([Image(ib,width=cw-10,height=ih)])
            except: inn.append([Paragraph(w["word"].upper()[:3],_pn("fb",fontName="Helvetica-Bold",fontSize=30,alignment=TA_CENTER,leading=38,textColor=d))])
            inn.append([Paragraph(f"<b>{w['word'].upper()}</b>",_pn("wd",fontName="Helvetica-Bold",fontSize=15,textColor=d,alignment=TA_CENTER,leading=18))])
            inn.append([Paragraph(f"🇫🇷 {w['french']}",_pn("tr",fontName="Helvetica",fontSize=11,textColor=d,alignment=TA_CENTER,leading=14))])
            ci=Table(inn,colWidths=[cw-10],rowHeights=[ih,1.1*cm,.9*cm])
            ci.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                ("BACKGROUND",(0,1),(0,1),colors.white),("BACKGROUND",(0,2),(0,2),l),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER")]))
            outer=Table([[ci]],colWidths=[cw])
            outer.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.white),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
                ("BOX",(0,0),(-1,-1),2,m),("ROUNDEDCORNERS",[10])]))
            row.append(outer)
        t=Table([row],colWidths=[cw+.6*cm,cw])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
        story.append(t)
    story.append(PageBreak())
    rng=random.Random(sum(w["id"] for w in words))
    L=[w["word"] for w in words[:5]]; R=[w["french"] for w in words[:5]]; Rs=R[:]; rng.shuffle(Rs)
    story.append(_bn(fl,f"Exercices · {ti.split(' · ')[0]}","Lis et écris !",d,m))
    story.append(Spacer(1,.4*cm))
    mt=Table([[f"  {a}","  ─────  ",f"  {b}"] for a,b in zip(L,Rs)],colWidths=[5.5*cm,3*cm,5.5*cm])
    mt.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),11),
        ("TEXTCOLOR",(0,0),(0,-1),d),("TEXTCOLOR",(2,0),(2,-1),m),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[l,_b("#f9fafb")]),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),8)]))
    story.extend([mt,Spacer(1,.25*cm)])
    story.append(Paragraph("<b>2.</b>  Complète les phrases :",_pn("ex",fontName="Helvetica-Bold",fontSize=12,textColor=_b("#1e3a8a"),spaceBefore=10,spaceAfter=3,leading=18)))
    bk="  |  ".join(f"<b>{w['word']}</b>" for w in words[:4])
    story.append(Paragraph(f"Banque : {bk}",_pn("tp",fontName="Helvetica-Oblique",fontSize=10,textColor=_b("#14532d"),leading=14,spaceAfter=4)))
    sents={"english":["The ________ is my favourite.","I see a big ________.","I have a ________ at home."],"spanish":["Me gusta el __________.","Veo un __________ grande.","Tengo un __________ en casa."]}
    for s in sents.get(lang,[]):
        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;▶  {s}",_pn("bd",fontName="Helvetica",fontSize=11,textColor=colors.black,leading=16,spaceAfter=4)))
        story.append(_al(""))
    story.append(Spacer(1,.2*cm))
    story.append(Paragraph("<b>3.</b>  🔊 Dis 3× à voix haute :",_pn("ex",fontName="Helvetica-Bold",fontSize=12,textColor=_b("#1e3a8a"),spaceBefore=10,spaceAfter=3,leading=18)))
    rp="  ·  ".join(w["word"] for w in words[5:8])
    rt=Table([[rp]],colWidths=[CW])
    rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),l),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),18),("TEXTCOLOR",(0,0),(-1,-1),d),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1),20),("ROUNDEDCORNERS",[8])]))
    story.extend([rt,Spacer(1,.3*cm)])
    ln={"english":"anglais","spanish":"espagnol"}[lang]
    story.append(Paragraph(f"<b>4.</b>  Traduis en {ln} :",_pn("ex",fontName="Helvetica-Bold",fontSize=12,textColor=_b("#1e3a8a"),spaceBefore=10,spaceAfter=3,leading=18)))
    for w in words[7:10]:
        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{w['french']}  →",_pn("bd",fontName="Helvetica",fontSize=11,textColor=colors.black,leading=16,spaceAfter=4)))
        story.append(_al(""))
    story.extend([Spacer(1,.4*cm),_st(f"🌟 {ti.split(' · ')[0]} terminé !"),PageBreak()])
    return story

def _msec(day,topic,raw):
    dk,mn,lt=_b("#1e3a8a"),_b("#2563eb"),_b("#dbeafe")
    s=[_bn("⭐","MATHÉMATIQUES",f"Thème : {topic[:60]}",dk,mn),Spacer(1,.5*cm)]
    for i,ex in enumerate(_pe(raw,5),1):
        bg=lt if i%2==0 else _b("#f9fafb")
        bt=Table([[Paragraph(f"<b>Exercice {i}.</b>&nbsp; {ex}",_pn("bd",fontName="Helvetica",fontSize=11,textColor=colors.black,leading=16,spaceAfter=4))]],colWidths=[CW])
        bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),14),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("ROUNDEDCORNERS",[6])]))
        s.extend([bt,_al(f"Ex {i} :"),Spacer(1,.1*cm)])
    s.extend([_st("⭐ Maths terminées !"),PageBreak()]); return s

def _lsec(day,topic,raw):
    dk,mn,lt=_b("#14532d"),_b("#16a34a"),_b("#dcfce7")
    s=[_bn("🧠","LOGIQUE & RAISONNEMENT",f"Thème : {topic[:60]}",dk,mn),Spacer(1,.5*cm)]
    for i,ex in enumerate(_pe(raw,4),1):
        bg=lt if i%2==0 else _b("#f9fafb")
        bt=Table([[Paragraph(f"<b>Puzzle {i}.</b>&nbsp; {ex}",_pn("bd",fontName="Helvetica",fontSize=11,textColor=colors.black,leading=16,spaceAfter=4))]],colWidths=[CW])
        bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LEFTPADDING",(0,0),(-1,-1),14),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),("ROUNDEDCORNERS",[6])]))
        s.extend([bt,_al(f"Puzzle {i} :"),Spacer(1,.18*cm)])
    s.extend([_st("🧠 Logique terminée !"),PageBreak()]); return s

def _bilan(day):
    d,m,l=_b("#3730a3"),_b("#6d28d9"),_b("#ede9fe")
    s=[_bn("🌟","BILAN DU JOUR","Tu as tout fait ? Bravo champion !",d,m),Spacer(1,.8*cm)]
    sm=[["","Section","Durée","Fait ?","⭐"],["⭐","Mathématiques","20 min","☐","☆ ☆ ☆ ☆ ☆"],
        ["🧠","Logique","15 min","☐","☆ ☆ ☆ ☆ ☆"],["🇬🇧","Anglais","20 min","☐","☆ ☆ ☆ ☆ ☆"],
        ["🇪🇸","Espagnol","20 min","☐","☆ ☆ ☆ ☆ ☆"],["🌙","Arabe","15 min","☐","☆ ☆ ☆ ☆ ☆"]]
    t=Table(sm,colWidths=[1*cm,8*cm,2.5*cm,2*cm,5*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),d),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),("LEFTPADDING",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[l,colors.white]),("GRID",(0,0),(-1,-1),.5,_b("#e5e7eb"))]))
    s.append(t); s.append(Spacer(1,1*cm))
    sd=[["✍️ Signature du parent :","___________________________","📅 Date :","_______________"]]
    st=Table(sd,colWidths=[5*cm,6*cm,2.5*cm,4*cm])
    st.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),12),("TOPPADDING",(0,0),(-1,-1),6)]))
    s.append(st); s.append(Spacer(1,.6*cm))
    ft=Table([[Paragraph(f"🚀 <b>{day}/200 jours accomplis !</b>  {200-day} restants — continue comme ça !",_pn("fg",fontName="Helvetica-Bold",fontSize=13,textColor=d,leading=18))]],colWidths=[CW])
    ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),l),("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),("LEFTPADDING",(0,0),(-1,-1),16),("ROUNDEDCORNERS",[8])]))
    s.append(ft); return s


# ═══════════════════ SECTION ARABE COMPLÈTE ══════════════════════
def _arsec(words,day):
    KD,KM,KL,KLL=_b("#831843"),_b("#db2777"),_b("#fce7f3"),_b("#fdf2f8")
    story=[]
    # Bannière vocab
    bt=Table([[Paragraph("🌙  اللغة العربية",_pn("at",fontName="Helvetica-Bold",fontSize=16,textColor=colors.white,leading=20)),
               Paragraph("مفردات اليوم — Sans traduction FR, Arabic only",_pn("as",fontName="Helvetica-Oblique",fontSize=10,textColor=_b("#e5e7eb"),leading=13))]],
             colWidths=[9*cm,CW-9*cm])
    bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),KD),("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROUNDEDCORNERS",[8])]))
    story.extend([bt,Paragraph("📌  Regarde l'image, prononce le mot arabe, répète 3 fois à voix haute",
        _pn("nt",fontName="Helvetica-Oblique",fontSize=10,textColor=KD,leading=13,spaceAfter=8,spaceBefore=6))])
    # Cartes vocab arabe — sans traduction FR
    cw,ch=8.2*cm,7.5*cm; ih=ch-3.0*cm
    for i in range(0,len(words),2):
        row=[]
        for j in range(2):
            if i+j>=len(words): row.append(Spacer(cw,ch)); continue
            w=words[i+j]; aw=_ar(w["word"]); ph=PHON.get(w["word"],"")
            ib=gimg(w["word_en"],w["word"],w["french"],w["cat"],"arabic",200)
            inn=[]
            try: inn.append([Image(ib,width=cw-10,height=ih)])
            except: inn.append([Paragraph("🖼️",_pn("fb",fontName="Helvetica",fontSize=38,alignment=TA_CENTER,leading=46))])
            inn.append([Paragraph(aw,_pn("aw",fontName="KacstB",fontSize=26,textColor=KD,alignment=TA_CENTER,leading=32))])
            inn.append([Paragraph(f"({ph})" if ph else " ",_pn("ph",fontName="Helvetica-Oblique",fontSize=9,textColor=_b("#6b7280"),alignment=TA_CENTER,leading=12))])
            ci=Table(inn,colWidths=[cw-10],rowHeights=[ih,1.0*cm,0.6*cm])
            ci.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                ("BACKGROUND",(0,1),(0,1),colors.white),("BACKGROUND",(0,2),(0,2),KLL),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER")]))
            outer=Table([[ci]],colWidths=[cw])
            outer.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.white),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
                ("BOX",(0,0),(-1,-1),2,KM),("ROUNDEDCORNERS",[10])]))
            row.append(outer)
        t=Table([row],colWidths=[cw+.6*cm,cw])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),
            ("RIGHTPADDING",(0,0),(-1,-1),0),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
        story.append(t)
    story.append(PageBreak())

    # Page écriture guidée
    wb=Table([[Paragraph("✍️  تدريب على الكتابة — Écriture guidée",_pn("h",fontName="Helvetica-Bold",fontSize=15,textColor=colors.white,leading=20,alignment=TA_CENTER))]],colWidths=[CW])
    wb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),KD),("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),14),("ROUNDEDCORNERS",[8])]))
    story.extend([wb,Spacer(1,.4*cm)])
    story.append(Paragraph("🖊️  Trace le modèle gris puis écris seul — L'arabe s'écrit de <b>droite à gauche ←</b>",
        _pn("i",fontName="Helvetica",fontSize=11,textColor=KD,leading=14,spaceAfter=8)))
    # Lettres du jour
    phase=min(6,(day-1)//8+1); letters=ARALPHA.get(phase,ARALPHA[1])
    lc=[]
    for lt,name,snd in letters[:5]:
        lc.append(Table([[Paragraph(_ar(lt),_pn("ll",fontName="KacstB",fontSize=28,textColor=KM,alignment=TA_CENTER,leading=34)),
            Paragraph(f"/{snd}/  {name}",_pn("ln",fontName="Helvetica",fontSize=8,textColor=_b("#6b7280"),alignment=TA_CENTER,leading=12))]],
            colWidths=[2*cm,1.4*cm],style=TableStyle([("BACKGROUND",(0,0),(-1,-1),KLL),
                ("BOX",(0,0),(-1,-1),1,KM),("ROUNDEDCORNERS",[6]),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE")])))
    while len(lc)<5: lc.append(Spacer(3.4*cm,2*cm))
    story.append(Paragraph("📖 <b>Lettres du jour :</b>",_pn("ll2",fontName="Helvetica-Bold",fontSize=11,textColor=KD,spaceAfter=5)))
    story.extend([Table([lc],colWidths=[CW//5]*5,style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),8)])),Spacer(1,.3*cm)])
    # Exercices écriture
    for idx,w in enumerate(words[:5],1):
        aw=_ar(w["word"]); ph=PHON.get(w["word"],"")
        story.append(Table([[Paragraph(f"<b>{idx}.</b>  {w['word']}  {'('+ph+')' if ph else ''}",_pn("wh",fontName="KacstR",fontSize=13,textColor=KD,leading=16)),
            Paragraph("← droite à gauche",_pn("dir",fontName="Helvetica-Oblique",fontSize=9,textColor=_b("#6b7280"),alignment=TA_RIGHT,leading=12))]],colWidths=[CW*0.65,CW*0.35]))
        ex=Table([[Paragraph(aw,_pn("m",fontName="KacstB",fontSize=38,textColor=_b("#e0b4cb"),alignment=TA_CENTER,leading=48))],
                  [Paragraph(aw+" · "+aw,_pn("g",fontName="KacstB",fontSize=26,textColor=_b("#edd9e8"),alignment=TA_CENTER,leading=34))],
                  [Paragraph(" ",_pn("e",fontName="KacstR",fontSize=22,leading=30))]],colWidths=[CW])
        ex.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),KLL),("BACKGROUND",(0,1),(0,1),_b("#fff8fb")),
            ("BACKGROUND",(0,2),(0,2),colors.white),("BOX",(0,2),(0,2),0.5,_b("#ddd")),
            ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("ROUNDEDCORNERS",[5])]))
        story.extend([ex,Spacer(1,.22*cm)])
    story.append(PageBreak())

    # Page activités
    ab=Table([[Paragraph("🎯  أنشطة تعليمية — Activités",_pn("h",fontName="Helvetica-Bold",fontSize=15,textColor=colors.white,leading=20,alignment=TA_CENTER))]],colWidths=[CW])
    ab.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),KD),("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),14),("ROUNDEDCORNERS",[8])]))
    story.extend([ab,Spacer(1,.4*cm)])
    rng=random.Random(day+1000); sample=words[:5]
    rs=[w["word"] for w in sample]; rng.shuffle(rs)
    story.append(Paragraph("1️⃣  <b>رَبِّطْ — Relie le mot arabe à l'image</b>",_pn("e1",fontName="Helvetica-Bold",fontSize=12,textColor=KD,spaceBefore=5,spaceAfter=8,leading=16)))
    CAT_ICONS={"fruits":"🍎🍊🍋🍇🍓","vegetables":"🥕🍅🥦🌽🥒","animals":"🐱🐶🐰🐴🐄","wild_animals":"🦁🐯🐘🦒🦓","sea":"🐬🦈🐙🦀🐳","birds":"🦅🦉🦚🦜🦢","food":"🍕🍔🎂🍝🥗","drinks":"💧🥛🍵☕🍹","body":"👁️👂✋💪❤️","colors":"🔴🔵🟡🟢🟣","clothes":"👕👖👗👟👒","home":"🏠🛏️🪑💡📺","school":"📚✏️📓🎒✂️","transport":"🚗🚌🚂✈️🚲","nature":"☀️🌙⭐🌧️🌳","family":"👩👨👧👦👵","sports":"⚽🏀🎾🏊🚴","emotions":"😊😢😠😨🤩","actions":"🏃⬆️🚶🎤✍️","adjectives":"🐘🐭🦒🏎️🐢","places":"🏙️🌳🛒🏥🍽️"}
    mr=[]
    for i,(lw,rw) in enumerate(zip(sample,rs)):
        cat=lw["cat"]; icons=list(CAT_ICONS.get(cat,"📌📌📌📌📌")); icon=icons[i%len(icons)]
        mr.append([Paragraph(_ar(lw["word"]),_pn("ml",fontName="KacstB",fontSize=16,textColor=KD,alignment=TA_CENTER,leading=20)),
                   Paragraph("— →",_pn("da",fontName="Helvetica",fontSize=12,textColor=_b("#ccc"),alignment=TA_CENTER)),
                   Paragraph(f"{icon}  {_ar(rw)}",_pn("mr2",fontName="KacstB",fontSize=14,textColor=KM,alignment=TA_CENTER,leading=18))])
    mt=Table(mr,colWidths=[5.5*cm,4*cm,5.5*cm])
    mt.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[KLL,colors.white]),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8),("BOX",(0,0),(-1,-1),0.5,_b("#f0d0e4"))]))
    story.extend([mt,Spacer(1,.4*cm)])
    # Lettres manquantes
    story.append(Paragraph("2️⃣  <b>أكمل الكلمة — Complète le mot arabe</b> ✏️",_pn("e2",fontName="Helvetica-Bold",fontSize=12,textColor=KD,spaceBefore=5,spaceAfter=8,leading=16)))
    miss=[]
    for w in words[5:9]:
        wd=w["word"]; mid=len(wd)//2
        gapped=wd[:mid]+" ___ "+wd[mid+1:] if len(wd)>=3 else wd[0]+" ___ "
        miss.append([Paragraph(_ar(gapped),_pn("gp",fontName="KacstB",fontSize=18,textColor=KD,alignment=TA_CENTER,leading=24)),
                     Paragraph("→",_pn("ar",fontName="Helvetica",fontSize=14,textColor=_b("#6b7280"),alignment=TA_CENTER)),
                     Paragraph("___________",_pn("ans",fontName="Helvetica",fontSize=14,textColor=_b("#ccc"),alignment=TA_CENTER))])
    mt2=Table(miss,colWidths=[7*cm,1.5*cm,6.5*cm])
    mt2.setStyle(TableStyle([("ROWBACKGROUNDS",(0,0),(-1,-1),[KLL,colors.white]),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8),("BOX",(0,0),(-1,-1),0.5,_b("#f0d0e4"))]))
    story.extend([mt2,Spacer(1,.4*cm)])
    # Dessine et écris
    story.append(Paragraph("3️⃣  <b>ارسم واكتب — Dessine et écris le mot</b> 🎨",_pn("e3",fontName="Helvetica-Bold",fontSize=12,textColor=KD,spaceBefore=5,spaceAfter=8,leading=16)))
    dc=[]
    for w in words[:3]:
        aw=_ar(w["word"])
        box_top=Table([[" "]],colWidths=[5.5*cm],style=TableStyle([("BOX",(0,0),(-1,-1),1,KM),("ROUNDEDCORNERS",[8]),("TOPPADDING",(0,0),(-1,-1),32),("BOTTOMPADDING",(0,0),(-1,-1),32)]))
        box_bot=Table([[" "]],colWidths=[5.5*cm],style=TableStyle([("BOX",(0,0),(-1,-1),0.5,_b("#ddd")),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
        cell=Table([[box_top],[Paragraph(aw,_pn("dw",fontName="KacstB",fontSize=18,textColor=KD,alignment=TA_CENTER,leading=24,spaceBefore=4))],[Paragraph("اكتب الكلمة ↓",_pn("sub",fontName="KacstR",fontSize=8,textColor=_b("#6b7280"),alignment=TA_CENTER,leading=12))],[box_bot]],colWidths=[5.5*cm])
        dc.append(cell)
    while len(dc)<3: dc.append(Spacer(5.5*cm,3*cm))
    story.extend([Table([dc],colWidths=[CW/3]*3,style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)])),Spacer(1,.4*cm)])
    # Intrus arabe
    story.append(Paragraph("4️⃣  <b>الدخيل — Trouve l'intrus parmi les 4 mots arabes</b> 🔍",_pn("e4",fontName="Helvetica-Bold",fontSize=12,textColor=KD,spaceBefore=5,spaceAfter=8,leading=16)))
    by_cat={}
    for w in words: by_cat.setdefault(w["cat"],[]).append(w)
    cats=[c for c,ws in by_cat.items() if len(ws)>=3][:2]
    if len(cats)>=2:
        grp=by_cat[cats[0]][:3]+[by_cat[cats[1]][0]]; rng.shuffle(grp)
        ic=[Paragraph(f"{i}. {_ar(w['word'])}",_pn("ic",fontName="KacstB",fontSize=15,textColor=KD,leading=20,alignment=TA_CENTER)) for i,w in enumerate(grp,1)]
        it=Table([ic],colWidths=[CW/4]*4)
        it.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),KLL),("BOX",(0,0),(-1,-1),0.5,KM),
            ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("LEFTPADDING",(0,0),(-1,-1),5),("ROUNDEDCORNERS",[8])]))
        story.extend([it,Paragraph("L'intrus est le numéro : _______    Parce que : ___________________",_pn("rep",fontName="Helvetica",fontSize=11,textColor=_b("#6b7280"),leading=16,spaceBefore=8))])
    story.extend([Spacer(1,.4*cm),_st("🌙 Arabe terminé ! Colorie tes étoiles :"),PageBreak()])
    return story


# ═══════════════════ GÉNÉRATION PDF PRINCIPAL ════════════════════
def generate_pdf(day,words_by_lang,math_topic,logic_topic,exercises_html=""):
    today=datetime.now().strftime("%A %d %B %Y")
    pct=round(day/200*100,1)
    buf=io.BytesIO()
    def footer(cv,doc):
        cv.saveState()
        cv.setFillColor(_b("#3730a3")); cv.rect(0,0,W,1.2*cm,fill=1,stroke=0)
        cv.setFillColor(colors.white); cv.setFont("Helvetica",8)
        cv.drawString(1.5*cm,.45*cm,f"🎓 Prof Agent · Jour {day}/200 · {today}")
        cv.drawRightString(W-1.5*cm,.45*cm,f"Page {doc.page}")
        cv.restoreState()
    def cov_draw(cv,doc): _cov(cv,day,today,pct,words_by_lang)
    class _PDoc(BaseDocTemplate):
        def __init__(self,buf,**kw):
            super().__init__(buf,**kw)
            self.addPageTemplates([
                PageTemplate(id="cover",frames=[Frame(0,0,W,H,id="cv")],onPage=cov_draw),
                PageTemplate(id="main",frames=[Frame(1.5*cm,2*cm,W-3*cm,H-3.5*cm,id="m")],onPage=footer),
            ])
    doc=_PDoc(buf,pagesize=A4); story=[NextPageTemplate("main"),PageBreak()]
    for lg in ["english","spanish"]:
        story.extend(_vsec(lg,words_by_lang.get(lg,[])))
    story.extend(_arsec(words_by_lang.get("arabic",[]),day))
    story.extend(_msec(day,math_topic,exercises_html))
    story.extend(_lsec(day,logic_topic,exercises_html))
    story.extend(_bilan(day))
    doc.build(story)
    return buf.getvalue()


# ═══════════════════ EXERCICES GROQ ══════════════════════════════
def gen_ex(day,words):
    mt=MATH[min(day-1,len(MATH)-1)]; lt=LOGIC[min(day-1,len(LOGIC)-1)]
    ph=1 if day<=50 else 2 if day<=100 else 3 if day<=150 else 4
    wl=lambda lg:", ".join(f"{w['word']}({w['french']})" for w in words.get(lg,[])[:6])
    prompt=f"""Professeur pour enfant 6 ans. JOUR {day}/200 Phase {ph}.
MATHS — {mt}:
1. [exercice concret avec situation réelle]
2. [calcul progressif]
3. [problème appliqué]
4. [défi mental]
5. [problème contextualisé]
LOGIQUE — {lt}:
1. [puzzle logique simple]
2. [suite ou séquence]
3. [énigme]
4. [raisonnement]
EN: {wl("english")}  ES: {wl("spanish")}  AR: {wl("arabic")}
Texte pur numéroté uniquement. Pas de HTML ni markdown."""
    try:
        r=Groq(api_key=GROQ_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            temperature=0.82,max_tokens=2500)
        return r.choices[0].message.content
    except Exception as e:
        log.error(f"Groq: {e}"); return ""


# ═══════════════════ ENVOI EMAIL ══════════════════════════════════
def send_email(day,pdf_bytes):
    now=datetime.now(MOROCCO).strftime("%d/%m/%Y") if MOROCCO else "—"
    fname=f"Prof_Jour_{day:03d}_{now.replace('/','')}.pdf"
    subj=f"🎓 Leçon Jour {day}/200 · {now} · EN+ES+AR+Maths+Logique"
    sz=len(pdf_bytes)//1024
    body=f"""<div style="font-family:Arial,sans-serif;max-width:580px;margin:0 auto;background:#f0f4ff;padding:20px;border-radius:16px">
<div style="background:linear-gradient(135deg,#3730a3,#6d28d9);border-radius:12px;padding:24px;text-align:center;color:white">
<div style="font-size:48px">🎓</div><h1 style="margin:8px 0;font-size:24px">Professeur du Jour</h1>
<p>Jour {day}/200 · {now}</p>
<div style="background:rgba(255,255,255,.2);border-radius:20px;padding:5px 16px;display:inline-block;margin-top:8px;font-size:13px">📎 PDF {sz} KB · Emojis illustrés · Arabe calligraphié</div>
</div>
<div style="background:white;border-radius:12px;padding:16px;margin-top:12px">
<table style="width:100%;border-spacing:4px;border-collapse:separate"><tr>
<td style="background:#dbeafe;border-radius:8px;padding:8px;text-align:center;font-size:12px;font-weight:bold">⭐ Maths<br>20 min</td>
<td style="background:#dcfce7;border-radius:8px;padding:8px;text-align:center;font-size:12px;font-weight:bold">🧠 Logique<br>15 min</td>
<td style="background:#fee2e2;border-radius:8px;padding:8px;text-align:center;font-size:12px;font-weight:bold">🇬🇧 Anglais<br>20 min</td>
<td style="background:#fce7f3;border-radius:8px;padding:8px;text-align:center;font-size:12px;font-weight:bold">🇪🇸 Espagnol<br>20 min</td>
<td style="background:#f3e5f5;border-radius:8px;padding:8px;text-align:center;font-size:12px;font-weight:bold">🌙 Arabe<br>15 min</td>
</tr></table></div>
<p style="text-align:center;color:#6b7280;font-size:11px;margin-top:12px">🤖 Professeur Agent v5 · Envoi automatique 19h00 Maroc</p></div>"""
    if GMAIL_USER and GMAIL_PASS:
        try:
            msg=MIMEMultipart("mixed")
            msg["From"]=f"Prof de Sami <{GMAIL_USER}>"; msg["To"]=EMAIL_TO; msg["Subject"]=subj
            msg.attach(MIMEText(body,"html"))
            p=MIMEBase("application","pdf"); p.set_payload(pdf_bytes)
            encoders.encode_base64(p)
            p.add_header("Content-Disposition",f'attachment; filename="{fname}"')
            msg.attach(p)
            with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=30) as s:
                s.login(GMAIL_USER,GMAIL_PASS); s.send_message(msg)
            log.info(f"✅ Gmail → {EMAIL_TO}"); return True
        except Exception as e: log.error(f"Gmail: {e}")
    if RESEND_KEY:
        try:
            import resend as rs; rs.api_key=RESEND_KEY
            rs.Emails.send({"from":EMAIL_FROM,"to":[EMAIL_TO],"subject":subj,"html":body,
                "attachments":[{"filename":fname,"content":list(pdf_bytes)}]})
            log.info(f"✅ Resend → {EMAIL_TO}"); return True
        except Exception as e: log.error(f"Resend: {e}")
    log.error("⚠️  Aucun fournisseur email (GMAIL ou RESEND)"); return False


# ═══════════════════ SCHEDULER + MAIN ════════════════════════════
def run_daily():
    day=tday()
    if day is None: log.info(f"Programme non actif (début={START_DATE})"); return
    log.info(f"════════ JOUR {day}/200 ════════")
    words=wday(day)
    if not words: log.error("Pas de mots"); return
    mt=MATH[min(day-1,len(MATH)-1)]; lt=LOGIC[min(day-1,len(LOGIC)-1)]
    log.info(f"  Maths  : {mt[:45]}"); log.info(f"  Logique: {lt[:45]}")
    log.info(f"  EN sample: {[w['word'] for w in words.get('english',[])[:4]]}...")
    log.info("  [1/3] Exercices Groq...")
    ex=gen_ex(day,words)
    log.info("  [2/3] Génération PDF...")
    pdf=generate_pdf(day,words,mt,lt,ex)
    log.info(f"  PDF: {len(pdf)//1024} KB")
    log.info("  [3/3] Envoi email...")
    send_email(day,pdf)
    log.info(f"════════ FIN JOUR {day} ════════")

def main():
    if not EMAIL_TO:
        log.error("❌ PROFESSOR_EMAIL_TO non défini"); raise SystemExit(1)
    if not (GMAIL_USER or RESEND_KEY):
        log.error("❌ GMAIL_USER+GMAIL_APP_PASSWORD ou RESEND_API_KEY requis"); raise SystemExit(1)
    log.info("╔══════════════════════════════════════════════╗")
    log.info("║   PROFESSEUR AGENT v5 — Fichier unique       ║")
    log.info(f"║   Début: {START_DATE}  →  {EMAIL_TO}   ║")
    log.info("║   Envoi : 19h00 Maroc chaque jour           ║")
    log.info("╚══════════════════════════════════════════════╝")
    if os.environ.get("PROFESSOR_TEST")=="1":
        log.info("🧪 Mode TEST — envoi immédiat"); run_daily(); return
    last=None
    while True:
        try:
            now=datetime.now(MOROCCO)
            if now.hour==19 and now.minute==0 and last!=now.date():
                last=now.date(); run_daily()
        except Exception as e: log.error(f"Erreur: {e}",exc_info=True)
        time.sleep(30)

if __name__=="__main__": main()
