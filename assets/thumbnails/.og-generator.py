"""OG 썸네일(1200x630) 생성기.

POSTS 에 항목을 추가하고 실행하면 이 디렉터리에 og<key>.html 이 생성된다.
HTML 을 1200x630 뷰포트로 캡처한 뒤 jpg 로 변환해서 쓴다.

    python3 assets/thumbnails/.og-generator.py
    cd assets/thumbnails && python3 -m http.server 4399
    # 브라우저를 1200x630 으로 띄워 og<key>.html 캡처 -> preview.png
    sips -s format jpeg -s formatOptions 88 preview.png --out <포스트파일명>.jpg

포스트 frontmatter 에 아래를 추가하면 jekyll-seo-tag 가 og:image 로 잡아준다.

    image:
      path: "/assets/thumbnails/<포스트파일명>.jpg"

한글은 Pretendard 로 렌더링된다(로컬 설치 폰트).
"""

import os

# key, 큰제목, 부제, 하단 메타, 상단 라벨, 그라디언트 시작색, 끝색
POSTS = [
    ("s1", "시즌 1", "『대규모 시스템 설계 기초』", "2025.09 – 11 · 전 8회",
     "K-DEVCON 시스템 디자인 스터디", "#1e3a5f", "#0f1c2e"),
    ("s2", "시즌 2", "『대규모 시스템 설계 기초 2』 1~6장", "2025.12 – 2026.02 · 전 6회",
     "K-DEVCON 시스템 디자인 스터디", "#1f3d3a", "#0d1f1d"),
    ("s3", "시즌 3", "『대규모 시스템 설계 기초 2』 7~13장", "2026.02 – 04 · 전 7회",
     "K-DEVCON 시스템 디자인 스터디", "#3a2a4d", "#1a1226"),
    ("pg", "PostgreSQL", "VACUUM &amp; VACUUM FULL", "MVCC · dead tuple · bloat · autovacuum",
     "스터디-데이터베이스", "#1d3f4a", "#0c1f26"),
    ("muse", "Muse Code", "PR 코드리뷰 액션 교체기", "Claude Opus 5 → Muse Spark 1.3 · 리뷰 1회 15원",
     "GitHub Actions", "#2b2f6b", "#12142e"),
]

# 큰제목이 길면 h1 폰트를 줄인다
def h1_size(text):
    return 118 if len(text) <= 7 else 96

TPL = """<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1200px;height:630px;overflow:hidden}
.card{position:relative;width:1200px;height:630px;
  background:radial-gradient(120%% 140%% at 12%% 0%%, %(c1)s 0%%, %(c2)s 62%%, #070b12 100%%);
  font-family:Pretendard,'Apple SD Gothic Neo',sans-serif;color:#fff;
  display:flex;flex-direction:column;justify-content:center;padding:0 82px}
svg.net{position:absolute;inset:0;width:100%%;height:100%%;opacity:.17}
.label{display:inline-flex;align-items:center;gap:10px;font-size:25px;font-weight:600;
  letter-spacing:.02em;color:#cfe0f5;opacity:.92;margin-bottom:24px}
.label .dot{width:11px;height:11px;border-radius:50%%;background:#5aa9f7;
  box-shadow:0 0 14px 3px rgba(90,169,247,.65)}
h1{font-size:%(h1)dpx;font-weight:800;line-height:1;letter-spacing:-.02em;
  text-shadow:0 4px 26px rgba(0,0,0,.55)}
.book{margin-top:26px;font-size:41px;font-weight:700;color:#eaf2fb;
  text-shadow:0 2px 14px rgba(0,0,0,.5)}
.rule{width:96px;height:5px;border-radius:3px;background:#5aa9f7;margin:34px 0 22px;
  box-shadow:0 0 16px 2px rgba(90,169,247,.5)}
.meta{font-size:27px;font-weight:500;color:#a8bdd6}
.site{position:absolute;right:82px;bottom:52px;font-size:25px;font-weight:600;color:#8fa8c4}
</style></head><body><div class="card">
<svg class="net" viewBox="0 0 1200 630" fill="none">
 <g stroke="#8ec5ff" stroke-width="1.5">
  <path d="M905 92 L1058 178 M1058 178 L1010 340 M1010 340 L1112 452 M905 92 L1010 340
           M1058 178 L1148 300 M1010 340 L888 470 M888 470 L1005 566 M1112 452 L1005 566
           M888 470 L762 402 M905 92 L790 196 M790 196 L888 470 M1148 300 L1112 452"/>
 </g>
 <g fill="#bfe0ff">
  <circle cx="905" cy="92" r="9"/><circle cx="1058" cy="178" r="7"/><circle cx="1010" cy="340" r="11"/>
  <circle cx="1112" cy="452" r="7"/><circle cx="888" cy="470" r="9"/><circle cx="1005" cy="566" r="7"/>
  <circle cx="1148" cy="300" r="6"/><circle cx="790" cy="196" r="6"/><circle cx="762" cy="402" r="6"/>
 </g>
</svg>
<div class="label"><span class="dot"></span>%(label)s</div>
<h1>%(title)s</h1>
<div class="book">%(sub)s</div>
<div class="rule"></div>
<div class="meta">%(meta)s</div>
<div class="site">jonghoonpark.com</div>
</div></body></html>"""

d = os.path.dirname(os.path.abspath(__file__))
for key, title, sub, meta, label, c1, c2 in POSTS:
    html = TPL % dict(title=title, sub=sub, meta=meta, label=label,
                      c1=c1, c2=c2, h1=h1_size(title))
    open(f"{d}/og{key}.html", "w").write(html)
    print("wrote", f"{d}/og{key}.html")
