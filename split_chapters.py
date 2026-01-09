#!/usr/bin/env python3
"""
TXT 파일을 회차별로 분할하는 스크립트

사용법:
    python split_chapters.py                    # 대화형 메뉴
    python split_chapters.py novel.txt          # CLI 모드
    python split_chapters.py novel.txt --group-size 10
    python split_chapters.py novel.txt --preset korean_hanja
    python split_chapters.py novel.txt --pattern "===\\s*\\d+화\\s*==="
"""

import re
import argparse
import sys
from pathlib import Path
from tkinter import Tk, filedialog


# 프리셋 패턴 정의
PRESETS = {
    "korean": r"#?\s*제\d+장",           # # 제1장, 제12장
    "korean_hanja": r"第\d+章",           # 第1章, 第100章
    "chapter_en": r"[Cc]hapter\s*\d+",    # Chapter 1, chapter 001
    "chapter_num": r"[Cc]h\.?\s*\d+",     # Ch.1, ch 5
    "episode": r"[Ee]p\.?\s*\d+",         # Ep.1, EP 10
    "part": r"[Pp]art\s*\d+",             # Part 1, PART 5
}

PRESET_DESCRIPTIONS = {
    "korean": "# 제1장, 제12장 (한글)",
    "korean_hanja": "第1章, 第100章 (한자)",
    "chapter_en": "Chapter 1, chapter 001 (영문)",
    "chapter_num": "Ch.1, ch 5 (축약)",
    "episode": "Ep.1, EP 10 (에피소드)",
    "part": "Part 1, PART 5 (파트)",
}


def parse_chapters(text: str, pattern: str) -> list[tuple[str, str]]:
    """
    정규식 패턴으로 텍스트를 회차별로 분할

    Args:
        text: 전체 텍스트
        pattern: 회차 구분 정규식 패턴

    Returns:
        [(회차제목, 내용), ...] 형태의 리스트
    """
    # 패턴으로 모든 회차 시작점 찾기
    matches = list(re.finditer(pattern, text))

    if not matches:
        print(f"경고: 패턴 '{pattern}'에 매칭되는 회차를 찾을 수 없습니다.")
        return []

    chapters = []
    for i, match in enumerate(matches):
        title = match.group()
        start = match.start()

        # 다음 회차 시작점까지 또는 끝까지
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        content = text[start:end]
        chapters.append((title, content))

    return chapters


def group_chapters(chapters: list[tuple[str, str]], group_size: int) -> list[list[tuple[str, str]]]:
    """
    회차들을 지정한 개수씩 그룹화

    Args:
        chapters: [(회차제목, 내용), ...] 리스트
        group_size: 그룹당 회차 수

    Returns:
        [[(회차1), (회차2), ...], [(회차6), ...], ...] 형태
    """
    groups = []
    for i in range(0, len(chapters), group_size):
        groups.append(chapters[i:i + group_size])
    return groups


def extract_chapter_number(title: str) -> str:
    """회차 제목에서 숫자 추출"""
    numbers = re.findall(r"\d+", title)
    return numbers[0] if numbers else "0"


def save_groups(
    groups: list[list[tuple[str, str]]],
    base_name: str,
    output_dir: Path
) -> list[Path]:
    """
    그룹화된 회차들을 파일로 저장

    Args:
        groups: 그룹화된 회차 리스트
        base_name: 원본 파일명 (확장자 제외)
        output_dir: 출력 디렉토리

    Returns:
        생성된 파일 경로 리스트
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for group in groups:
        if not group:
            continue

        # 첫 회차와 마지막 회차 번호 추출
        first_num = extract_chapter_number(group[0][0])
        last_num = extract_chapter_number(group[-1][0])

        # 파일명 생성: 원본명_제1-5장.txt
        filename = f"{base_name}_제{first_num}-{last_num}장.txt"
        filepath = output_dir / filename

        # 내용 합치기
        content = "\n".join(ch[1] for ch in group)

        # 파일 저장
        filepath.write_text(content, encoding="utf-8")
        saved_files.append(filepath)
        print(f"생성: {filepath}")

    return saved_files


def select_file() -> Path | None:
    """파일 선택 다이얼로그"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    file_path = filedialog.askopenfilename(
        title="분할할 TXT 파일 선택",
        filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
    )

    root.destroy()

    if file_path:
        return Path(file_path)
    return None


def interactive_menu() -> int:
    """대화형 메뉴 모드"""
    print("=" * 50)
    print("    TXT 파일 회차별 분할 도구")
    print("=" * 50)
    print()

    # 1. 파일 선택
    print("[1단계] 파일 선택")
    print("파일 선택 창이 열립니다...")
    input_file = select_file()

    if not input_file:
        print("파일을 선택하지 않았습니다.")
        return 1

    print(f"선택된 파일: {input_file}")
    print()

    # 2. 패턴 선택
    print("[2단계] 회차 구분 형식 선택")
    print("-" * 40)
    preset_keys = list(PRESETS.keys())
    for i, key in enumerate(preset_keys, 1):
        print(f"  {i}. {PRESET_DESCRIPTIONS[key]}")
    print(f"  {len(preset_keys) + 1}. 직접 입력 (정규식)")
    print("-" * 40)

    while True:
        try:
            choice = input(f"선택 (1-{len(preset_keys) + 1}) [기본값: 1]: ").strip()
            if choice == "":
                choice = 1
            else:
                choice = int(choice)

            if 1 <= choice <= len(preset_keys):
                pattern = PRESETS[preset_keys[choice - 1]]
                break
            elif choice == len(preset_keys) + 1:
                pattern = input("정규식 패턴 입력: ").strip()
                if not pattern:
                    print("패턴을 입력해주세요.")
                    continue
                break
            else:
                print("올바른 번호를 선택해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

    print(f"선택된 패턴: {pattern}")
    print()

    # 3. 그룹 크기 선택
    print("[3단계] 몇 회차씩 묶을지 선택")
    print("-" * 40)
    print("  1. 5회차씩")
    print("  2. 10회차씩")
    print("  3. 20회차씩")
    print("  4. 30회차씩")
    print("  5. 50회차씩")
    print("  6. 100회차씩")
    print("  7. 직접 입력")
    print("-" * 40)

    group_options = [5, 10, 20, 30, 50, 100]

    while True:
        try:
            choice = input("선택 (1-7) [기본값: 1]: ").strip()
            if choice == "":
                group_size = 5
                break
            else:
                choice = int(choice)

            if 1 <= choice <= 6:
                group_size = group_options[choice - 1]
                break
            elif choice == 7:
                group_size = int(input("회차 수 입력: ").strip())
                if group_size < 1:
                    print("1 이상의 숫자를 입력해주세요.")
                    continue
                break
            else:
                print("올바른 번호를 선택해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

    print(f"선택된 그룹 크기: {group_size}회차씩")
    print()

    # 실행
    print("=" * 50)
    print("분할 시작...")
    print("=" * 50)

    # 파일 읽기
    print(f"파일 읽는 중: {input_file}")
    text = input_file.read_text(encoding="utf-8")

    # 회차별 파싱
    print(f"패턴으로 분할 중: {pattern}")
    chapters = parse_chapters(text, pattern)

    if not chapters:
        input("\n엔터를 누르면 종료합니다...")
        return 1

    print(f"총 {len(chapters)}개 회차 발견")

    # 그룹화
    groups = group_chapters(chapters, group_size)
    print(f"{group_size}개씩 {len(groups)}개 그룹으로 분할")

    # 저장
    output_dir = input_file.parent
    base_name = input_file.stem
    saved_files = save_groups(groups, base_name, output_dir)

    print()
    print("=" * 50)
    print(f"완료! {len(saved_files)}개 파일 생성됨")
    print(f"저장 위치: {output_dir}")
    print("=" * 50)

    input("\n엔터를 누르면 종료합니다...")
    return 0


def cli_mode() -> int:
    """CLI 모드"""
    parser = argparse.ArgumentParser(
        description="TXT 파일을 회차별로 분할합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
프리셋 패턴:
  korean       #?제N장 형식 (기본값)
  korean_hanja 第N章 형식 (한자)
  chapter_en   Chapter N 형식
  chapter_num  Ch.N 형식
  episode      Ep.N 형식
  part         Part N 형식

예시:
  python split_chapters.py                              # 대화형 메뉴
  python split_chapters.py novel.txt
  python split_chapters.py novel.txt --group-size 10
  python split_chapters.py novel.txt --preset korean_hanja
  python split_chapters.py novel.txt --pattern "===\\s*\\d+화\\s*==="
        """
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="분할할 TXT 파일 경로"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default=None,
        help="회차 구분 정규식 패턴 (프리셋보다 우선)"
    )
    parser.add_argument(
        "--preset",
        type=str,
        choices=list(PRESETS.keys()),
        default="korean",
        help="프리셋 패턴 선택 (기본값: korean)"
    )
    parser.add_argument(
        "--group-size",
        type=int,
        default=5,
        help="그룹당 회차 수 (기본값: 5)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="출력 디렉토리 (기본값: 입력 파일과 같은 위치)"
    )

    args = parser.parse_args()

    # 입력 파일 확인
    if not args.input_file.exists():
        print(f"오류: 파일을 찾을 수 없습니다: {args.input_file}")
        return 1

    # 패턴 결정 (--pattern이 우선)
    pattern = args.pattern if args.pattern else PRESETS[args.preset]

    # 출력 디렉토리 결정
    output_dir = args.output_dir if args.output_dir else args.input_file.parent

    # 파일 읽기
    print(f"파일 읽는 중: {args.input_file}")
    text = args.input_file.read_text(encoding="utf-8")

    # 회차별 파싱
    print(f"패턴으로 분할 중: {pattern}")
    chapters = parse_chapters(text, pattern)

    if not chapters:
        return 1

    print(f"총 {len(chapters)}개 회차 발견")

    # 그룹화
    groups = group_chapters(chapters, args.group_size)
    print(f"{args.group_size}개씩 {len(groups)}개 그룹으로 분할")

    # 저장
    base_name = args.input_file.stem
    saved_files = save_groups(groups, base_name, output_dir)

    print(f"\n완료! {len(saved_files)}개 파일 생성됨")
    return 0


def main():
    # 인자 없이 실행하면 대화형 메뉴
    if len(sys.argv) == 1:
        return interactive_menu()
    else:
        return cli_mode()


if __name__ == "__main__":
    exit(main())
