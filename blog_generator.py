import os
import sys
import re
from pathlib import Path
import webbrowser
os.chdir(sys.path[0])
def get_file_detail(filename):
    t = open(filename,'r').read().replace('\n',' ')
    title = re.search('(?<=<title>).*(?=</title>)',t).group()
    date = re.search('(?<=<date>).*(?=</date>)',t).group()
    content = re.search('(?<=<content>).*(?=</content>)',t).group()
    sample = re.search('(?<=<sample>).*(?=</sample>)',t)
    if sample:
        sample = sample.group()
    else:
        sample = content[:100]
    sample += '......'

    return title,date,content,sample

def generate_index_html(data,fname,page):#产生类似首页的简要目录的html
    data.sort(key = lambda x:x[1])
    data.reverse()
    f = '\n'.join([d[0] for i,d in enumerate(data)])
    main_index_template = page.replace('<!--articles-->',f)
    open(fname,'w').write(main_index_template)
def generate_main():
    main_index_template = open('index_template.html','r').read()
    essay_template = open('essay_template.html','r').read()
    main_article = '''
                                    <article class="meta" itemscope="" itemtype="http://schema.org/BlogPosting">
                    <header>
                        <a href="{url}" itemprop="url"><h2 itemprop="name headline">{title}</h2></a>
                    </header>
                    <main>
                                                <p itemprop="articleBody">
                            {simple_content}                   </p>
                    </main>
                    <footer>
                        <span class="comments">{date}发表</span>
                                            </footer>
                </article>'''
    main_arc_list = []
    for url in ['informal_essay']:
        p = Path(url)
        txt_files = p.glob('*.xml')
        session_essay_list =[]

        session_index_template = p/'index_template.html'
        if session_index_template.exists():
            session_index_template = session_index_template.read_text()
        else:
            session_index_template = main_index_template
        
        session_essay_template = p/'essay_template.html'
        if session_essay_template.exists():
            session_essay_template = session_essay_template.read_text()
        else:
            session_essay_template = essay_template

        for j in txt_files:
            title, date, content, sample = get_file_detail(j)
            k = main_article.format(title = title,
                date = date,
                url = '/{session}/{article}'.format(session=url,article = j.with_suffix('.html').name),
                simple_content = sample)
            main_arc_list.append((k,date))
            session_essay_list.append((k,date))

            f = session_essay_template.format(
                title = title,
                date = date,
                content = content,
                comment_id = "'{}_{}'".format(url,j.with_suffix('').name)
            )
            #generate a article page
            open(j.with_suffix('.html'),'w').write(f)
        #generate a article catalogue for the 'url' section
        filename = Path(url) / 'index.html'
        generate_index_html(session_essay_list,filename,page = session_index_template)
    generate_index_html(main_arc_list,'index.html',page = main_index_template)
    update_m4a_list()
def update_m4a_list():
    #更新m4a列表
    m4a_suffix = {'.m4a','.mp3'}
    m4a_path = Path(sys.path[0]) / 'm4a'
    js_header = '''let player = new cplayer({
element: document.getElementById('app'),
playlist: ['''
    m4a_list = []
    for i in m4a_path.glob('*'):
        if i.suffix in m4a_suffix:
            if i.suffix == '.mp3':
                m4a_name = i.with_suffix('.m4a')
                os.system('ffmpeg -i "{}" "{}" -y'.format(i,m4a_name))
                os.remove(i)
                i = m4a_name 
            os.system('git add "./m4a/{}"'.format(i.name))
            stem = i.stem.split('-')
            if len(stem) == 2:
                author = stem[0]
                name = stem[1]
            else:
                author = ''
                name = stem[0]
            stem = '-'.join(stem)
            if i.with_suffix('.jpg').exists():
                poster = i.with_suffix('.jpg').name 
            else: 
                poster = 'poster.jpg'
            
            ele = {'src':'/m4a/'+i.name,'name':name,'artist':author,'lyric':'','sublyric':'',
                   'poster':'/m4a/'+poster,}
            m4a_list.append(ele)
    fp = open(m4a_path/'playlist.js','w')
    fp.write(js_header)
    f = ['\n    {\n'+ '\n'.join(["    {}: '{}',".format(k,v) for k,v in i.items()]) + '\n    },\n' for i in m4a_list]
    fp.write(''.join(f))
    fp.write('\n]\n})')
    fp.close()
    os.system('git add ./m4a/playlist.js')

if __name__=='__main__':
    generate_main()
    webbrowser.open('http://127.0.0.1:8000/index.html')
    os.system('python -m http.server')
   
