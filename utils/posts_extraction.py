import re
import asyncio


async def photo_links_extractor(post_content):
    to_find = re.compile(r'(?<=<a href=")(.+?)(?=" imageanchor=)')
    links = re.findall(to_find, post_content)
    if links:
        return links
    else:
        return False


async def text_extractor(post_content):
    pattern = r'(<div.+?/div>)|(<script async.+?;\n*</script>)|(<span.+?<u>|</u.+?<br />*\n*<br />*)|(<a name=\'more\'></a><br />\n*)|(<span.+?<i>|</i.+?<br />*\n*<br />*)'
    to_find = re.compile(pattern, flags=re.DOTALL)
    text_fragments = re.sub(to_find, '', post_content)
    print(text_fragments)
    exit()

sample_post = \
    ('''
Sernik krówkowy bez pieczenia to deser na zimno przygotowany w tortownicy, z dodatkiem serka, cukru, słodkiej śmietanki oraz masy krówkowej (kajmakowej).&nbsp; Całość nie jest mocno słodka, gdyż poza masą krówkową, do sernika dodałam tylko niewielką ilość cukru waniliowego.<br />
Przepis można wykorzystać <b>w tortownicy o średnicy 21cm</b>.<br />
<br />
<div class="separator" style="clear: both; text-align: center;">
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhO6GM9nIKHyiaBsKc9tTHEsc5Ju20vej62Ntb0JXUZFViXGR8ui-bGOHjJZYNrWqWi4rKw8gcnomchi-XXo_Lk1zFDmjtv1okzEfr9fiMW44qU5x3m8kJwwrlBvKlPCjn33FZF8Kix2G4/s1600/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25281%2529.jpg" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img alt="Sernik bez pieczenia" border="0" data-original-height="990" data-original-width="660" height="640" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhO6GM9nIKHyiaBsKc9tTHEsc5Ju20vej62Ntb0JXUZFViXGR8ui-bGOHjJZYNrWqWi4rKw8gcnomchi-XXo_Lk1zFDmjtv1okzEfr9fiMW44qU5x3m8kJwwrlBvKlPCjn33FZF8Kix2G4/s640/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25281%2529.jpg" title="Sernik krówkowy" width="426" /></a></div>
<script async="" src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- wtresci -->
<br />
<ins class="adsbygoogle" data-ad-client="ca-pub-8884265346253106" data-ad-format="auto" data-ad-slot="8074171613" data-full-width-responsive="true" style="display: block;"></ins><script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
<a name='more'></a><br />
<span style="font-size: x-large;"><b><u>Sernik krówkowy bez pieczenia</u></b></span><br />
<br />
<span style="font-size: large;"><span style="color: #660000;"><b><i>Składniki:</i></b></span></span><br />
<br />
800g serka do sernika (z wiaderka, niezbyt gęstego)<br />
350-400g masy krówkowej (kajmakowej)<br />
150g śmietanki 30%<br />
3 łyżeczki domowego cukru waniliowego<br />
24g (6 łyżeczek) żelatyny<br />
100ml wody<br />
biszkopty na spód (u mnie około 70g) <br />
<br />
2-3 łyżki masy krówkowej, 1 łyżeczka masła i 2-3 kostki gorzkiej czekolady do dekoracji<br />
<br />
<div class="separator" style="clear: both; text-align: center;">
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjbmIMEhQsHiP_M3ygeVSdSLGleH64Z5r3jRRkdrDL3k3oMwH6RCMfxxwbny-1-neclaiMA5tH1T7oJ_SxBdJi4P40VopmAfcZ3ipHi0S6I23UCOTUFUZFqoV-ehlDk8hzb4sqXCECsoYE/s1600/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25284%2529.jpg" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img alt="Sernik z masą krówkową" border="0" data-original-height="990" data-original-width="660" height="640" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjbmIMEhQsHiP_M3ygeVSdSLGleH64Z5r3jRRkdrDL3k3oMwH6RCMfxxwbny-1-neclaiMA5tH1T7oJ_SxBdJi4P40VopmAfcZ3ipHi0S6I23UCOTUFUZFqoV-ehlDk8hzb4sqXCECsoYE/s640/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25284%2529.jpg" title="Sernik na zimno z masą krówkową" width="426" /></a></div>
<br />
<span style="color: #660000;"><span style="font-size: large;"><b><i>Wykonanie:</i></b></span></span><br />
<br />
- tortownicę wyłożyć na dnie papierem do pieczenia, wyjmując go poza obręcz<br />
- do boku formy przykleić za pomocą masła pasek z papieru do pieczenia<br />
- na dno formy wyłożyć obok siebie biszkopty, można połamać je na kawałki, uzupełniając wolne pola<br />
<br />
<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- wtresci -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8884265346253106"
     data-ad-slot="8074171613"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
<br />
- do miski przełożyć serek i masę krówkową (kajmakową), zmiksować<br />
- żelatynę zalać wodą, odstawić do zgęstnienia, a następnie podgrzać ją krótko w kuchence mikrofalowej, aż się rozpuści (ja podgrzewam 5-10 sek., sprawdzam, czy już jest rzadka i podgrzewam ponownie)<br />
<br />
<div class="separator" style="clear: both; text-align: center;">
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj9_VthZF9STBbMwZ9XDiSducMAfP9S-iJlt2NgOtIDzB0JoTSqw45n8kBdx9vJfddCy-LYQg1Q8ZbjVaU9KgE93KwKpJanAYyjYvA4hloaz9-LIkMbMEheewYNnqkFv_VaHWRtYMkFlz8/s1600/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25285%2529.jpg" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img alt="Sernik kajmakowy bez pieczenia" border="0" data-original-height="990" data-original-width="660" height="640" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj9_VthZF9STBbMwZ9XDiSducMAfP9S-iJlt2NgOtIDzB0JoTSqw45n8kBdx9vJfddCy-LYQg1Q8ZbjVaU9KgE93KwKpJanAYyjYvA4hloaz9-LIkMbMEheewYNnqkFv_VaHWRtYMkFlz8/s640/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25285%2529.jpg" title="Sernik krówkowy bez pieczenia" width="426" /></a></div>
<br />
- gorącą żelatynę wstępnie ostudzić<br />
- do lekko ciepłej, ale ciągle płynnej, dodać 1 łyżkę masy serowej, dokładnie wymieszać do uzyskania jednolitej rzadkiej konsystencji<br />
- tak zahartowaną żelatynę wlać do masy serowej, zmiksować<br />
- śmietankę i cukier waniliowy przełożyć do naczynia, ubić na sztywno<br />
- ubitą śmietanę wmieszać do masy serowej<br />
- masę przełożyć na przygotowane biszkopty (delikatnie, żeby biszkopty się nie poprzesuwały), wyrównać, schłodzić w lodówce przez kilka godzin do zastygnięcia (najlepiej przez całą noc)<br />
<script async="" src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- wtresci -->
<br />
<ins class="adsbygoogle" data-ad-client="ca-pub-8884265346253106" data-ad-format="auto" data-ad-slot="8074171613" data-full-width-responsive="true" style="display: block;"></ins><script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
<br />
<div class="separator" style="clear: both; text-align: center;">
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg3uV7R4CLmFt5o0t1JV7BePF3P8oTQID-lde8NXeU15qYvJKeGMuLlCL2P36mtPNFso7GKVu1g37JaA5DFvgR36DjRguOn4LbJIqYE0HGX_fTF6n9LvGgekEVApu5rIE8lfldXGaICkmk/s1600/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25286%2529.jpg" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img alt="Sernik kajmakowy na zimno" border="0" data-original-height="990" data-original-width="660" height="640" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg3uV7R4CLmFt5o0t1JV7BePF3P8oTQID-lde8NXeU15qYvJKeGMuLlCL2P36mtPNFso7GKVu1g37JaA5DFvgR36DjRguOn4LbJIqYE0HGX_fTF6n9LvGgekEVApu5rIE8lfldXGaICkmk/s640/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25286%2529.jpg" title="Sernik krówkowy na zimno" width="426" /></a></div>
<br />
- ścięty sernik wyjąć z formy, udekorować<br />
- masę krówkową i masło podgrzać w kąpieli wodnej, aż stanie się bardziej płynna, zdjąć na blat, lekko przestudzić<br />
- lejącą się masą krówkową udekorować wierzch sernika, robiąc na nim esy floresy<br />
- zimną gorzką czekoladę zetrzeć, posypać nią wierzch sernika<br />
- całość ponownie schłodzić, przechowywać w lodówce<br />
<br />
<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- wtresci -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8884265346253106"
     data-ad-slot="8074171613"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
<br />
<div class="separator" style="clear: both; text-align: center;">
<a href="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj1HBgflPZY9GgnPpU6FpIPuoMwcC-AquZEDJEHhQHMcyht05bZSxNmzLcIz9jvEQtV637Avi-u_R-_7gcZKucovH_WVaTJrN9zfDQCm3A_L1iDeX6tTw8QB2R6tpOyG3bD85RbvAxzzSQ/s1600/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25282%2529.jpg" imageanchor="1" style="margin-left: 1em; margin-right: 1em;"><img alt="Sernik krówkowy" border="0" data-original-height="990" data-original-width="660" height="640" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj1HBgflPZY9GgnPpU6FpIPuoMwcC-AquZEDJEHhQHMcyht05bZSxNmzLcIz9jvEQtV637Avi-u_R-_7gcZKucovH_WVaTJrN9zfDQCm3A_L1iDeX6tTw8QB2R6tpOyG3bD85RbvAxzzSQ/s640/Sernik+kr%25C3%25B3wkowy+bez+pieczenia+%25282%2529.jpg" title="Sernik kajmakowy" width="426" /></a></div>
    ''')


async def main_test():
    photos = await text_extractor(sample_post)
    for link in photos:
        print(link)


if __name__ == '__main__':
    asyncio.run(main_test())
