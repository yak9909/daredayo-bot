import discord
import re


client = discord.Client()
kusodomains_map = {
    "https://soude.su/"                     : r'そう(です|(わ|だ)?よ)',
    "https://imanona.si/"                   : r'(いま|今)の(な|無)し',
    "https://mouyuru.site/"                 : r'(もう)?(ゆる|許)して(ください)?',
    "https://iyado.su/"                     : r'(や|いや|嫌)(だ|です|どす)',
    "https://nasa.so/"                      : r'(な|無)さそう',
    "https://otsu.care/"                    : r'(乙|(お(つか|疲)れ(さま|様)?)|おつ|o2|02)',
    "https://yoroshiku.onegai.shim.earth/"  : r'((よろ|宜)(し(く|こ)(お(ねが|願)いします)?)?|4649)',
    "https://sounanokamoshiremasen.ga/"     : r'そう(なの)?(かも(しれ(ない(の)?|ません|ん)((だ)?が|けど)))',
    "https://ohayougozaima.su/"             : r'(お(はよ(う|ー)?|早う)(ございます)?|(お|起)き(た|ました))',
    "https://soujyanai.ga/"                 : r'((ちが|違)う|そうじゃ(な(い(が)?|くて(さ|ね)?|ね(え|ぇ|ー)(よ)?)))',
    "https://sorehako.ml/"                  : r'(それは)?(こま|困)る((ん|の)(だ|です)(が|けど))?',
    "https://shinchokuda.me/"               : r'(しんちょく|進捗)(だめ|ダメ)です(。)?'
}


@client.event
async def on_ready():
    print("ready")


@client.event
async def on_message(msg):
    for k,v in kusodomains_map.items():
        if re.match(v, msg.content):
            await msg.channel.send(k)


client.run("ODgxNTQwNTU4MjM2MDI0ODQz.YSuUnw.uvuxmTNQ8Zis08O6qbFGTEO6SXA")
