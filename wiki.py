import urllib.request
# Etuliite, josta linkit Wikipedian sisällä tunnistetaan
LINKKITUNNISTE = '<a href="/wiki/'
# Artikkelikohtaisten linkkilistojen "välimuisti"
LINKIT = {}
# Vastaavat tiedolle, löytyykö artikkelia
NOTEXISTING = '<b>Wikipediassa ei ole tämän nimistä artikkelia.</b>'
EXISTENCE = {}

# Muuntaa käyttäjän syöttämän / näkemän nimen linkeissä käytettyyn muotoon
def nimi2link(nimi):
    return nimi.replace(' ', '_').replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('Ö', '%C3%96').replace('Ä', '%C3%84')

# Edellisen käänteisfunktio
def link2nimi(link):
    return link.replace('_', ' ').replace('%C3%A4', 'ä').replace('%C3%B6', 'ö').replace('%C3%96', 'Ö').replace('%C3%84', 'Ä')

# Testaa, löytyykö annetunnimistä artikkelia
def exists(artikkeli):
    if artikkeli in EXISTENCE:
        return EXISTENCE[artikkeli]
    exists = True
    try:
        urllib.request.urlopen('https://fi.wikipedia.org/wiki/'+artikkeli)
    except urllib.error.HTTPError:
        exists = False
    EXISTENCE[artikkeli] = exists
    return exists

# Hakee artikkelin nimen perusteella artikkelit, joihin artikkelista on suora linkki
def artikkeli2linkit(artikkeli):
    # Käytetään ensisjaisesti välimuistia
    if artikkeli in LINKIT:
        return LINKIT[artikkeli]
    fp = urllib.request.urlopen('https://fi.wikipedia.org/wiki/'+artikkeli)
    str = fp.read().decode('utf-8')
    fp.close()
    nextlink = str.find(LINKKITUNNISTE)
    linkit = []
    while nextlink != -1:
        str = str[nextlink + len(LINKKITUNNISTE):]
        linkki = str[:str.find('"')]
        if len(linkki) != 0 and ':' not in linkki:
            linkit.append(linkki)
        nextlink = str.find(LINKKITUNNISTE)
    # Poistetaan tuplailmentymät linkeistä
    linkit = list(set(linkit))
    # Linkkilistat tallennetaan "välimuistiin"
    LINKIT[artikkeli] = linkit
    return linkit

'''
Etsii lyhyimmän reitin kahden artikkelin välillä linkkejä pitkin. Käytössä on "yksinkertaistettu" Dijkstran algoritmi, jossa
solmut ovat artikkeleita, linkit suunnattuja kaaria ja jokaisen kaaren pituus on sama.
'''
def reitti(a1, a2):
    # Minkä artikkelin kautta lyhyin reitti mihinkin artikkeliin on viimeksi kulkenut
    edeltajat = {}
    taso1 = [a1]
    taso2 = []
    while True:
        # Käydään ensisjaisesti läpi artikkelit, joiden linkkilista tunnetaan jo.
        taso1 = sorted(taso1, key=lambda x: 0 if x in LINKIT else 1)
        for a in taso1:
            for b in artikkeli2linkit(a):
                if b not in edeltajat:
                    edeltajat[b] = a
                else:
                    continue
                # Reitti löytyi
                if b == a2:
                    reitti = [a2]
                    while reitti[-1] != a1:
                        reitti.append(edeltajat[reitti[-1]])
                    # Algoritmi muodostaa listan takaperin
                    return list(reversed(reitti))
                taso2.append(b)
        taso1 = taso2
        taso2 = []
        # Kaikki epäsuorastikin linkitetyt artikkelit on käyty läpi, mutta reittiä ei löytynyt
        if len(taso1) == 0:
            return 'EI REITTIÄ'

# Pääohjelma
print('Wikipedian polunetsintä!')
while True:
    a1 = input('Artikkeli 1>')
    while not exists(nimi2link(a1)):
        print('Artikkelia {} ei vaikuta olevan.'.format(a1))
        a1 = input('Artikkeli 1>')
    a2 = input('Artikkeli 2>')
    while not exists(nimi2link(a2)):
        print('Artikkelia {} ei vaikuta olevan.'.format(a2))
        a2 = input('Artikkeli 2>')
    print('Etsitään...')
    r = reitti(nimi2link(a1), nimi2link(a2))
    if r == 'Ei reittiä':
        print('Reittiä ei löytynyt.')
    print('Reitti: ', ' -> '.join(list(map(link2nimi, r))))
    if input('Jatketaanko (k/e)?>') == 'e':
        break
