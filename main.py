import fitz
from pathlib import Path


def get_user_selection(items, item_type):
    """
    사용자에게 목록을 보여주고, 선택된 항목들의 리스트를 반환하는 공통 함수
    """
    if not items:
        print(f"❌ 선택 가능한 {item_type}이(가) 없습니다.")
        return []

    print(f"\n🔍 발견된 {item_type} 목록:")
    print("-" * 40)
    for idx, item in enumerate(items):
        info = item.name
        if item.is_dir():
            count = len(list(item.glob("*.png")))
            info = f"{item.name} (이미지 {count}장)"

        print(f" [{idx + 1}] {info}")
    print("-" * 40)

    print("👉 작업을 수행할 번호를 입력하세요.")
    print("   (예시: '1' 또는 '1 3 5' 처럼 띄어쓰기로 구분, 전체는 'all')")
    selection = input("입력 > ").strip()

    selected_items = []

    if selection.lower() == "all":
        selected_items = items
    else:
        try:
            # 쉼표(,)가 있으면 공백으로 바꾸고 분리
            indices = selection.replace(",", " ").split()
            for i in indices:
                idx = int(i) - 1  # 화면엔 1부터 보였으므로 0-based로 변환
                if 0 <= idx < len(items):
                    selected_items.append(items[idx])
        except ValueError:
            print("❌ 잘못된 입력입니다. 숫자만 입력해주세요.")
            return []

    if not selected_items:
        print("❌ 유효한 번호가 선택되지 않았습니다.")

    return selected_items


def pdf_to_images(dpi=300):
    """
    PDF 파일을 선택하여 이미지로 분해
    """
    current_dir = Path(".")
    pdf_files = [
        p for p in current_dir.glob("*.pdf") if not p.name.endswith("_converted.pdf")
    ]

    target_pdfs = get_user_selection(pdf_files, "PDF 파일")

    if not target_pdfs:
        return

    print(f"\n🚀 총 {len(target_pdfs)}개의 PDF 분해를 시작합니다.\n")

    for pdf_path in target_pdfs:
        try:
            print(f"▶ 처리 중: {pdf_path.name}")

            output_folder = current_dir / pdf_path.stem
            output_folder.mkdir(exist_ok=True)

            doc = fitz.open(pdf_path)
            for page in doc:
                pix = page.get_pixmap(dpi=dpi)
                filename = f"{page.number + 1:03d}.png"
                pix.save(output_folder / filename)

            print(f"   ✅ 완료! (저장 폴더: {output_folder})")

        except Exception as e:
            print(f"   ⚠️ 에러 발생 ({pdf_path.name}): {e}")

    print("\n🎉 선택한 PDF의 분해 작업이 끝났습니다!")


def images_to_pdf():
    """
    폴더를 선택하여 PDF로 병합 (파일명 + _converted.pdf)
    """
    current_dir = Path(".")

    candidate_folders = []
    for d in current_dir.iterdir():
        if d.is_dir() and list(d.glob("*.png")):
            candidate_folders.append(d)

    target_folders = get_user_selection(candidate_folders, "이미지 폴더")

    if not target_folders:
        return

    print(f"\n🚀 총 {len(target_folders)}개의 폴더 병합을 시작합니다.\n")

    for folder in target_folders:
        image_files = sorted(list(folder.glob("*.png")))

        output_filename = f"{folder.name}_converted.pdf"
        output_path = current_dir / output_filename

        print(f"▶ 병합 중: '{folder.name}' -> {output_filename}")

        try:
            doc = fitz.open()
            for img_path in image_files:
                img = fitz.open(img_path)
                pdfbytes = img.convert_to_pdf()
                img_pdf = fitz.open("pdf", pdfbytes)
                doc.insert_pdf(img_pdf)

            doc.save(output_path)
            print("   ✅ 저장 완료!")

        except Exception as e:
            print(f"   ⚠️ 에러 발생: {e}")

    print("\n🎉 선택한 폴더의 병합 작업이 끝났습니다!")


if __name__ == "__main__":
    while True:
        print("\n=== PDF 도구 모음 ===")
        print("1. PDF 분해 (선택한 PDF -> PNG)")
        print("2. PDF 병합 (선택한 폴더 -> PDF)")
        print("q. 종료")

        choice = input("선택 > ").strip().lower()

        if choice == "1":
            pdf_to_images()
        elif choice == "2":
            images_to_pdf()
        elif choice == "q":
            print("프로그램을 종료합니다.")
            break
        else:
            print("올바른 번호를 입력해주세요.")
