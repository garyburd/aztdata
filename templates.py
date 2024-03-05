import tags

script = """
(function() {
  let form = document.getElementById("download");
  let text = document.getElementById("text");
  let showuri =  function() {
    let fd = new FormData(form);
    let kvpairs = [];
    for (const pair of fd.entries()) {
      kvpairs.push(`${encodeURIComponent(pair[0])}=${encodeURIComponent(pair[1])}`);
    }
    let s = `${form.action}?${kvpairs.join("&")}`;
    text.textContent = s;
  }
  form.addEventListener("submit", showuri);
})();
"""


def index(write, passages, waypoints) -> None:
    d = tags.Document(write)
    d.printr('<!doctype html>')
    with d.HTML():
        with d.HEAD():
            d.META(charset='utf-8')
            d.META(
                content='width=device-width, initial-scale=1',
                name='viewport',
            )
            d.LINK(
                rel='shortcut icon',
                href='/static/favicon.ico',
                type='image/x-icon',
            )
            d.LINK(
                rel='stylesheet',
                href='/static/site.css',
            )
        with d.BODY():
            d.H1()('AZT Tracks')
            with d.P():
                with d.FORM(id='download', action='/download', method='get'):
                    d.LABEL(for_='start')('Start Passage: ')
                    with d.SELECT(name='start', id='start'):
                        for passage in passages:
                            d.OPTION(value=passage.passage)(
                                passage.formatted_name()
                            )
                    d.BR()
                    d.LABEL(for_='end')('End Passage: ')
                    with d.SELECT(name='end', id='end'):
                        d.OPTION(value=100)('To northern terminus')
                        d.OPTION(value=-3)('Start + 3')
                        d.OPTION(value=-2)('Start + 2')
                        d.OPTION(value=-1)('Start + 1')
                        d.OPTION(selected=True, value=0)('Same as start')
                        for passage in passages:
                            d.OPTION(value=passage.passage)(
                                passage.formatted_name()
                            )
                    d.BR()
                    with d.FIELDSET():
                        d.LEGEND()('Format')
                        d.INPUT(
                            type='radio',
                            id='formatgpx',
                            name='format',
                            value='gpx',
                            checked=True,
                        )
                        d.LABEL(for_='formatgpx')('GPX')
                        d.INPUT(
                            type='radio',
                            id='formatkml',
                            name='format',
                            value='kml',
                        )
                        d.LABEL(for_='formatkml')('KML')
                    with d.FIELDSET():
                        d.LEGEND()('Waypoints')
                        for index, name, checked in waypoints:
                            d.INPUT(
                                type='checkbox',
                                id=f'wp{index}',
                                name='wp',
                                value=index,
                                checked=checked,
                            )
                            d.LABEL(for_=f'wp{index}')(name)
                            d.BR()
                    d.INPUT(type='submit', value='Download')
            with d.P():
                d.SPAN(id='text')
            with d.SCRIPT():
                d.printr(script)


def gpx(write, name, passages, allowed_waypoint_types) -> None:
    _ = name
    d = tags.XDocument(write)
    d.printr('<?xml version="1.0" encoding="UTF-8"?>')
    with d.tag(
        'gpx', xmlns='http://www.topografix.com/GPX/1/1', version='1.1'
    ):
        for passage in passages:
            with d.tag('trk'):
                d.tag('name')(passage.formatted_name())
                with d.tag('trkseg'):
                    for p in passage.track():
                        with d.tag('trkpt', lat=p.lat, lon=p.lon):
                            d.tag('ele')(p.ele)
            for p in passage.waypoints(allowed_waypoint_types):
                with d.tag('wpt', lat=p.lat, lon=p.lon):
                    d.tag('ele')(p.ele)
                    d.tag('name')(p.name)
                    if p.comment:
                        d.tag('comment')(p.comment)
                    d.printr(
                        '<extensions><coros_type>19</coros_type><coros_flag>0</coros_flag></extensions>'
                    )


styles = """
<Style id="P1_highlight">
 <LineStyle><color>ff2f2fd3</color><width>4</width></LineStyle>
</Style>
<Style id="P1_normal">
 <LineStyle><color>ff2f2fd3</color><width>3</width></LineStyle>
</Style>
<StyleMap id="P1">
 <Pair><key>normal</key><styleUrl>#P1_normal</styleUrl></Pair>
 <Pair><key>highlight</key><styleUrl>#P1_highlight</styleUrl></Pair>
</StyleMap>

<Style id="P2_highlight">
 <LineStyle><color>ff9f3f30</color><width>4</width></LineStyle>
</Style>
<Style id="P2_normal">
 <LineStyle><color>ff9f3f30</color><width>3</width></LineStyle>
</Style>
<StyleMap id="P2">
 <Pair><key>normal</key><styleUrl>#P2_normal</styleUrl></Pair>
 <Pair><key>highlight</key><styleUrl>#P2_highlight</styleUrl></Pair>
</StyleMap>

<Style id="PA_highlight">
 <LineStyle><color>ff3c8e38</color><width>4</width></LineStyle>
</Style>
<Style id="PA_normal">
 <LineStyle><color>ff3c8e38</color><width>3</width></LineStyle>
</Style>
<StyleMap id="PA">
 <Pair><key>normal</key><styleUrl>#PA_normal</styleUrl></Pair>
 <Pair><key>highlight</key><styleUrl>#PA_highlight</styleUrl></Pair>
</StyleMap>
  
<Style id="Water_normal">
 <IconStyle>
  <scale>0.75</scale>
  <Icon><href>https://earth.google.com/earth/rpc/cc/icon?color=1976d2&amp;id=2346&amp;scale=4</href></Icon>
  <hotSpot x="64" y="128" xunits="pixels" yunits="insetPixels"/>
 </IconStyle>
</Style>
<Style id="Water_highlight">
 <IconStyle>
  <scale>0.9</scale>
  <Icon><href>https://earth.google.com/earth/rpc/cc/icon?color=1976d2&amp;id=2346&amp;scale=4</href></Icon>
  <hotSpot x="64" y="128" xunits="pixels" yunits="insetPixels"/>
 </IconStyle>
</Style>
<StyleMap id="Water">
 <Pair><key>normal</key><styleUrl>#Water_normal</styleUrl></Pair>
 <Pair><key>highlight</key><styleUrl>#Water_highlight</styleUrl></Pair>
</StyleMap>


<Style id="Other_normal">
 <IconStyle>
  <scale>0.75</scale>
  <Icon><href>https://earth.google.com/earth/rpc/cc/icon?color=ef5350&amp;id=2003&amp;scale=4</href></Icon>
  <hotSpot x="64" y="128" xunits="pixels" yunits="insetPixels"/>
 </IconStyle>
</Style>
<Style id="Other_highlight">
 <IconStyle>
  <scale>0.9</scale>
  <Icon><href>https://earth.google.com/earth/rpc/cc/icon?color=ef5350&amp;id=2003&amp;scale=4</href></Icon>
  <hotSpot x="64" y="128" xunits="pixels" yunits="insetPixels"/>
 </IconStyle>
</Style>
<StyleMap id="Other">
 <Pair><key>normal</key><styleUrl>#Other_normal</styleUrl></Pair>
 <Pair><key>highlight</key><styleUrl>#Other_highlight</styleUrl></Pair>
</StyleMap>
"""


def kml(write, name, passages, allowed_waypoint_types) -> None:
    d = tags.XDocument(write)
    d.printr('<?xml version="1.0" encoding="UTF-8"?>')
    with d.tag('kml', xmlns='http://www.opengis.net/kml/2.2'):
        with d.tag('Document'):
            d.tag('name')(name)
            d.tag('open')('1')
            d.printr(styles)
            for passage in passages:
                with d.tag('Folder'):
                    d.tag('name')(passage.formatted_name())
                    with d.tag('Placemark'):
                        d.tag('name')(passage.formatted_name())
                        d.tag('styleUrl')(f'#{passage.style()}')
                        with d.tag('MultiGeometry'):
                            with d.tag('LineString'):
                                d.tag('tesselate')('1')
                                with d.tag('coordinates'):
                                    for p in passage.track():
                                        d.printr(f'{p.lon},{p.lat},{p.ele}\n')
                with d.tag('Folder'):
                    d.tag('name')('Waypoints')
                    for p in passage.waypoints(allowed_waypoint_types):
                        with d.tag('Placemark'):
                            d.tag('name')(p.name)
                            if p.comment:
                                d.tag('description')(p.comment)
                            d.tag('styleUrl')(f'#{p.style()}')
                            with d.tag('Point'):
                                d.tag('coordinates')(
                                    f'{p.lon},{p.lat},{p.ele}'
                                )
