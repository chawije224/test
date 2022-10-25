async def getPSSHs():
    f = open('manifest.mpd', 'r').read()
    try:
        return f.split('urn:mpeg:cenc:',maxsplit=1)[-1].split('</cenc:pssh>')[0].split('>')[-1]
    except:
        return f.split('<cenc:pssh>',maxsplit=1)[-1].split('</cenc:pssh>')[0]