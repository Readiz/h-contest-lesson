# H 강의 사이트 요구사항

기준일은 2026-10-23이며 확인한 소스는 `d9522b25501e25ce9409427ddd7fd6033619276c`다. 이 문서는 강의 사이트의 제공 기능과 수용 조건을 정리한다. 강의 내용의 추가와 학습 순서는 [ROADMAP](../ROADMAP.md), 본문 검토 이력은 [LESSON_REVIEW](../LESSON_REVIEW.md), 작성 규칙은 [CONTRIBUTING](../CONTRIBUTING.md)이 기준이다.

공개 원본은 [GitHub Pages 카탈로그](https://git.readiz.com/h-contest-lesson/)다. h-contest의 로그인 후 강의 화면과 `/api/lessons`는 별도 `h-contest` 저장소의 소비 기능이다. 이 저장소 검사만으로 앱의 인증, 본문 렌더링, 문제 이동이 검증됐다고 표시하지 않는다.

## 기능 계약과 수용 조건

아래의 `구현 확인`은 소스 경로가 확인됐다는 의미다. 이번 문서 정리에서 운영 브라우저를 다시 검증했다는 뜻은 아니다.

| ID | 기능과 수용 조건 | 구현과 검사 근거 | 현재 상태 |
| --- | --- | --- | --- |
| LESSON-01 | `lessons.json`과 `lessons/`를 원본으로 사용한다. 강의 ID, 제목, 본문 경로, 하위 페이지와 분류가 일치하고 중복 ID와 저장소 밖 경로를 거부한다. | [manifest](../lessons.json), [validator](../scripts/validate_lessons.py) | 구현 확인 |
| LESSON-02 | 공개 카탈로그에 기본 및 심화 노트와 참고 노트를 구분하고, 난이도, 소요 시간, 성격, 구현 수준, 연습 상태를 실제 metadata대로 표시한다. `README.md`와 `index.html`은 같은 생성기에서 재생성 가능해야 한다. | [생성기](../scripts/generate_catalog.py), [카탈로그](../index.html), `generate_catalog.py --check` | 구현 확인 |
| LESSON-03 | 문제 신호별 길찾기, 심화 트랙, 선수/다음/관련 강의와 하위 페이지를 실제 존재하는 강의로 연결한다. 필수 선수 관계에 순환이 없어야 하며 같은 분류에서 선수가 먼저 온다. | 생성기의 `QUICK_GUIDES`, `TRACK_GUIDES`; validator의 관계 검사 | 구현 확인. h-contest 화면에서의 이동 검증은 별도 |
| LESSON-04 | 본문의 링크와 이미지가 실제 파일을 가리키고 이미지 대체 텍스트를 제공한다. `linked` 또는 `verified` 연습은 실제 문제나 입력, 과제, 확인 방법이 있는 로컬 연습을 갖춰야 한다. 미완성 후보는 ROADMAP에서 관리한다. | validator의 링크, 이미지, 연습 검사; [기초 예제 검사](../scripts/check_foundation_exercises.py) | 구현 확인. metadata의 `published`는 모든 추가 연습의 완성을 뜻하지 않음 |
| LESSON-05 | 제출용 코드와 일반 C++ 참고 예제의 환경을 구분한다. 공통 코드는 Markdown 원문에서 추출하며 배열 경계, 초기화, 차분, 재현성과 실제 기준값을 검사한다. | [공통 코드 검사](../scripts/check_cpp_basics.py), [제출 예제 검사](../scripts/check_submission_examples.py), [탐색 검사](../scripts/check_heuristic_search.py), [본문 예제 검사](../scripts/check_review_examples.py) | 검사 도구 구현 확인. 모든 예제의 실제 채점 성능을 보장하는 것은 아님 |
| LESSON-06 | 단계별 데모는 실제 모델 상태를 계산하고 이전, 다음, 재생, 처음, 진행 위치와 입력 변경을 제공한다. 기본 자동재생은 꺼져 있고 입력 변경, 마지막 단계, 숨겨진 페이지에서는 멈춘다. 설명은 색상 외의 텍스트로도 읽힌다. | [데모 앱](../demos/app.js), [계산 모델](../demos/models.js), [독립 기준값 검사](../scripts/check_demos.cjs) | 6종 구현 확인. 새 390px/1280px 시각 검수는 미실행 |
| LESSON-07 | 정적 원본을 공개하고 h-contest에는 검증된 데모를 복사한다. 앱 iframe은 `allow-scripts`만 허용하고 높이 메시지만 사용한다. 원본 Pages의 공개 범위와 앱의 로그인 제한을 구분한다. | [기여 절차의 데모 계약](../CONTRIBUTING.md), 데모의 `hcontest-lesson-demo-resize`; 앱의 동기화와 iframe은 별도 저장소 | 원본 계약 확인. 앱 복사본 일치와 sandbox는 이 저장소에서 재검증하지 않음 |
| LESSON-08 | 배포 전에 카탈로그 일치와 강의 검사를 통과한다. Pages는 `main` push 또는 수동 workflow로 배포하며 로컬 문서 커밋을 운영 배포로 간주하지 않는다. | [검사 workflow](../.github/workflows/validate.yml), [Pages workflow](../.github/workflows/pages.yml) | CI 설정 확인. 이번 작업은 push와 배포 없음 |

## 현재 범위와 남은 작업

2026-10-23 manifest에는 강의 98개와 하위 페이지 70개가 있다. 기본 및 심화 노트 31개, 참고 노트 67개이며 `practiceStatus`는 `linked` 46개, `todo` 52개다. 98개 모두 `published`지만, 이는 콘텐츠 공개 상태다. 추가 연습, 실행 검증의 범위, 교육 효과의 완료 상태와 합치지 않는다.

| 구분 | 남은 확인 또는 작업 | 완료 증거 |
| --- | --- | --- |
| 사이트 연결 | h-contest의 로그인 후 강의, 선수/다음/관련 이동, 문제 링크, 복사된 데모의 실제 동작 | 실제 사용자 인증 세션에서 본문과 이동 경로 확인. 공개 Pages 검사와 구분 |
| 화면 검증 | 카탈로그와 6종 데모의 모바일 폭, 키보드, 상태 설명, 입력 변경 | 390px와 1280px에서 처음/중간/마지막 상태, 재생 정지, 가로 넘침 확인 |
| 학습 콘텐츠 | SA 온도와 수락률 실험, SCHEDULX 연결, 이후 문제 단위 개편과 추가 연습 | ROADMAP의 해당 항목별 코드, 기준 답, 실제 문제 또는 완결형 로컬 과제 |
| 새 시각 자료 | ROADMAP에 기록된 후속 데모와 그림 | 실제 작은 입력과 상태 변화 검산. 그림 수를 늘린 것만으로 완료 처리하지 않음 |

검색, 학습 진도 저장, 개인 메모, 온라인 채점은 이 저장소의 구현 범위로 확인되지 않았다. 새 기능으로 요청받으면 별도 요구사항을 추가하며 기존 카탈로그의 완료 여부에 포함하지 않는다.

## 확인 방법과 이번 기록

저장소 루트에서 실행한다. Python, Node.js, C++17 및 ASan/UBSan이 필요하다.

```sh
python3 scripts/generate_catalog.py
python3 scripts/generate_catalog.py --check
python3 scripts/validate_lessons.py
```

README의 이 문서 링크는 생성기 `README_HEADER`에서 관리한다. 생성형 README를 직접 수정하지 않는다. 이번 작업에서는 문서와 생성기 링크를 추가했으며, 강의 본문, manifest, 데모와 운영 상태는 바꾸지 않았다.

2026-10-23 카탈로그 재생성 및 `--check`, 전체 validator를 통과했다. 강의 98개, 기초 연습 19개, STL 없는 코드 7개, 제출 흐름 28블록, ORDERING 탐색, 본문 조합과 경계 사례 48개, 데모 47,097개 assertion이 포함됐다. 새 브라우저 검사와 운영 배포는 수행하지 않았다.

## 2026-10-23 원격과 Pages 후속 점검

후속 점검 시작 시 로컬은 `a2adde3`, 원격 main과 마지막 성공한 Pages 배포는 `d9522b2`였다. 차이는 이 요구사항 문서와 README의 안내 링크 및 생성기 헤더뿐이고 강의, manifest와 데모 소스는 같았다. 공개 요구사항 문서가 404인 것도 이 미반영 커밋에 해당했다.

`generate_catalog.py --check`와 전체 `validate_lessons.py`를 다시 실행해 98개 강의와 위의 코드·데모 검사를 모두 통과했다. 이 문서 변경은 main push에 연결된 Validate Lessons와 Deploy GitHub Pages workflow로 반영하며, 완료 여부는 해당 커밋의 두 workflow 성공과 공개 문서·카탈로그 응답을 함께 확인한다. h-contest 앱 로그인과 물리 기기 동작은 이 배포 확인 범위에 포함하지 않는다.
