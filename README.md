# split-chapters

TXT 파일을 회차(장)별로 분할하는 Python 스크립트

## 설치

```bash
git clone https://github.com/route99-roadRunner/split-chapters.git
cd split-chapters
```

Python 3.10+ 필요 (외부 의존성 없음)

## 사용법

```bash
# 기본 사용 (5회차씩, # 제N장 패턴)
python split_chapters.py novel.txt

# 회차 수 지정
python split_chapters.py novel.txt --group-size 10
python split_chapters.py novel.txt --group-size 30
python split_chapters.py novel.txt --group-size 100

# 프리셋 패턴 사용
python split_chapters.py novel.txt --preset korean_hanja
python split_chapters.py novel.txt --preset chapter_en

# 커스텀 정규식 패턴
python split_chapters.py novel.txt --pattern "===\s*\d+화\s*==="

# 출력 디렉토리 지정
python split_chapters.py novel.txt --output-dir ./output
```

## 프리셋 패턴

| 프리셋 | 패턴 | 매칭 예시 |
|--------|------|-----------|
| `korean` (기본) | `#?\s*제\d+장` | `# 제1장`, `제12장` |
| `korean_hanja` | `第\d+章` | `第1章`, `第100章` |
| `chapter_en` | `[Cc]hapter\s*\d+` | `Chapter 1`, `chapter 001` |
| `chapter_num` | `[Cc]h\.?\s*\d+` | `Ch.1`, `ch 5` |
| `episode` | `[Ee]p\.?\s*\d+` | `Ep.1`, `EP 10` |
| `part` | `[Pp]art\s*\d+` | `Part 1`, `PART 5` |

## CLI 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `input_file` | 입력 TXT 파일 | (필수) |
| `--pattern` | 회차 구분 정규식 | - |
| `--preset` | 프리셋 패턴 선택 | `korean` |
| `--group-size` | 그룹당 회차 수 | `5` |
| `--output-dir` | 출력 디렉토리 | 입력 파일 위치 |

## 출력 파일명

`{원본파일명}_제{시작}-{끝}장.txt`

예시:
```
novel.txt (12개 장, 5개씩)
├── novel_제1-5장.txt
├── novel_제6-10장.txt
└── novel_제11-12장.txt
```

## License

MIT
