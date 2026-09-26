# Contributing

h-contest-lesson 저장소는 h-contest 휴리스틱 노트 콘텐츠의 source of truth입니다.

API와 공개 manifest는 이 저장소의 내용을 기준으로 제공됩니다.
따라서 레슨을 수정하거나 추가하려면 이 저장소에 Pull Request를 보내 주세요.

## 기여할 수 있는 내용

현재는 아래 기여를 환영합니다.

1. 오탈자, 맞춤법, 표현 개선
2. 설명이 불명확한 부분 보강
3. C++ 코드 예제 오류 수정
4. 이미지, 링크, 경로 오류 수정
5. 기존 레슨에 예제나 실수 포인트 추가
6. 새 레슨 추가

새 주제 후보와 아직 적절한 h-contest 문제가 없는 연습 문제는 [ROADMAP.md](ROADMAP.md)에 TODO로 관리합니다. 이미 공개된 레슨의 이동 기록과 보강 완료 기록은 [CHANGELOG.md](CHANGELOG.md)에 남깁니다.

## 레슨 수정 방법

기존 레슨은 아래 파일을 수정합니다.

```text
lessons/<lessonId>/lesson.md
```

길이가 긴 레슨은 `lesson.md`를 개요로 두고, 세부 본문을 하위 페이지로 나눌 수 있습니다.

```text
lessons/<lessonId>/pages/<page-id>.md
```

하위 페이지를 추가하거나 삭제하면 `lessons.json`의 해당 레슨에 `pages` 배열을 함께 갱신합니다.

페이지는 독립적인 학습 질문과 전제가 있을 때만 나눕니다. 글자 수나 하위 개념 개수만으로 분할하지 않습니다.

- 같은 알고리즘의 정의, 상태 변화 예시, 구현, 직접적인 활용은 한 본문에서 이어 설명합니다.
- 개요와 하위 본문 하나만 남았다면 하나의 강의로 합치는 것을 기본으로 합니다.
- 예제·연습이 앞의 설명을 바로 확인하는 역할이면 그 설명 옆에 둡니다.
- 서로 다른 문제 모델이나 독립적으로 찾아볼 구현은 별도 페이지로 둘 수 있습니다. 각 페이지는 다른 페이지의 중간 설명을 이어받지 않고 목적과 전제를 밝혀야 합니다.

통합할 때는 단순히 이어 붙이지 않고 중복 도입·선택표·결론을 정리합니다. 고유 예시와 구현 조건은 보존하고, manifest·본문 링크·검증 스크립트의 경로를 함께 갱신합니다.

예:

```text
lessons/dijkstra/lesson.md
lessons/segment-tree/lesson.md
```

## 새 레슨 추가 방법

새 레슨을 추가할 때는 아래 source 파일을 수정해 주세요.

```text
lessons/<new-lesson-id>/lesson.md
lessons.json
```

`lessons.json`에는 새 레슨이 들어갈 `folderId`, `level`, `estimatedMinutes`, `prerequisites`, `nextLessons`, `relatedLessons`를 함께 지정합니다. 하위 페이지가 있으면 `pageId`, `title`, `description`, `order`, `file`을 가진 `pages` 배열을 추가합니다.

`prerequisites`에는 실제 필수 지식만 넣고 선택 참고는 `relatedLessons`로 연결합니다. 선수 관계는 순환할 수 없으며, 같은 분류에서는 선수 레슨의 `order`가 더 작아야 합니다. validator가 두 조건을 검사합니다.

현재 공개 분류는 두 가지입니다.

- `heuristic-notes`: 휴리스틱 기본 및 심화 노트. 현재 h-contest 문제 풀이에 바로 쓰는 기본 구현, 모델링, 최적화, 검증 레슨만 들어갑니다.
- `heuristic-reference`: 휴리스틱 참고 노트. 현재 문제 풀이의 직접 범위를 넘는 전통 알고리즘, 이론, 희소 고급 도구, 장기 확장용 레퍼런스 레슨이 들어갑니다. 이 폴더에는 `research-reference`뿐 아니라 직접성이 낮은 `contest-core` 또는 `advanced-contest` 레슨도 들어갈 수 있습니다.

새 폴더를 추가하기보다 위 두 분류 중 하나를 먼저 고릅니다. 주제별 탐색은 `tags`, `difficultyAxes`, `prerequisites`, `nextLessons`, `relatedLessons`, 하위 `pages`로 표현합니다.

문서의 공개 성격이 명확하지 않으면 아래 metadata를 함께 지정합니다.

```json
{
  "status": "draft | review | published",
  "lessonType": "core | implementation | overview | reference | experimental",
  "seriesId": "parametric-optimization",
  "parentLessonId": "parametric-optimization",
  "practiceStatus": "none | todo | linked | verified",
  "implementationStatus": "concept-only | partial | full",
  "audience": "contest-core | advanced-contest | research-reference",
  "difficultyAxes": ["implementation | proof | modeling | selection"]
}
```

`difficultyAxes`는 레슨이 어려운 이유를 표시합니다. 코드와 corner case가 핵심이면 `implementation`, 조건 증명이 핵심이면 `proof`, 수학/그래프 모델로 바꾸는 과정이 핵심이면 `modeling`, 여러 기법 중 무엇을 고를지 판단하는 문서면 `selection`을 사용합니다. 둘 이상이 동시에 필요하면 여러 값을 넣습니다.

`published`인 `core` 또는 `implementation` 레슨은 `practiceStatus: todo` 상태로 둘 수 없습니다. 실제 practice 링크나 저장소 안의 로컬 완결형 연습을 준비한 뒤 정식 구현 레슨으로 올립니다. 실제 문제와 완전 구현이 아직 없으면 `overview` 또는 `reference`로 분류합니다.

이미지가 필요하면 아래 디렉터리에 추가합니다.

```text
lessons/<new-lesson-id>/lesson-assets/
```

그다음 아래 명령으로 파생 파일을 갱신하고 검증합니다.

```bash
python3 scripts/generate_catalog.py
python3 scripts/validate_lessons.py
```

학습 지도에 등록한 강의 ID가 manifest에 없으면 카탈로그 생성과 `--check`가 실패합니다. 강의를 통합하거나 삭제할 때 `QUICK_GUIDES`와 `TRACK_GUIDES`도 함께 갱신합니다.

아래 파일은 직접 편집하지 않고 생성 결과를 커밋합니다.

```text
README.md
index.html
```

`README.md`와 `index.html` 상단의 문제 신호별 빠른 길찾기, 심화 트랙 지도, 카드 배지 기준도 `scripts/generate_catalog.py`에서 생성됩니다. 새 허브 레슨을 추가하거나 기존 허브의 역할이 바뀌면 `QUICK_GUIDES`, `TRACK_GUIDES`, `METADATA_GUIDE`가 현재 학습 경로와 맞는지 함께 확인합니다.

새 레슨을 처음 작성할 때는 `templates/lesson.md`를 출발점으로 사용할 수 있습니다.

## lessonId 규칙

lessonId는 소문자 영어와 하이픈을 사용합니다.

좋은 예:

```text
zero-one-bfs
topological-sort
binary-lifting
```

피해야 할 예:

```text
ZeroOneBFS
0_1_BFS
한글-레슨
```

## 레슨 작성 스타일

직접 풀이 트랙(`heuristic-notes`)의 새 제출 예제는 h-contest 함수 구현형 `user.cpp`를 기준으로 작성합니다. STL과 표준 헤더를 쓰지 않고, 공개 API·고정 배열·직접 구현을 기본으로 합니다. `struct`, 참조, `template`는 사용 가능합니다. 일반 C++/STL이 필요한 참고 예제와 로컬 테스트 하네스는 적용 환경을 명시합니다. 기존 레슨의 전환은 ROADMAP 순서로 진행합니다.

C++가 있는 본문은 첫 코드 앞에 적용 환경을 표시합니다. 일반 C++17 학습용, h-contest 제출용·제출 확장용, 설계 조각을 구분하고, 문서 중간에 환경이 바뀌면 그 코드 옆에 다시 표시합니다. 설계 조각을 완성 제출로 소개하지 않으며, 일반 C++ 예제에는 [공통 코드로 옮기는 기준](lessons/cpp-common-library/lesson.md)을 연결합니다.

배열·난수·정렬·큐·힙의 공통 코드는 별도 [STL 없는 공통 라이브러리](lessons/cpp-common-library/lesson.md)를 원문으로 사용합니다. [제출 계약과 검증](lessons/cpp-contest-basics/lesson.md)은 문제를 풀기 시작하는 흐름을 다룹니다. 문제별 예제에는 필요한 블록 이름, 배열 상한, 인덱스 범위, TC 초기화 위치를 함께 적습니다. 설명 없이 거대한 템플릿을 전부 복사시키지 않습니다. 새 공통 코드가 필요하면 실제 사용 문제와 경계 검증을 함께 추가합니다.

공통 라이브러리와 제출 계약의 `cpp compile-check snippet=<name>` 블록은 `python3 scripts/check_cpp_basics.py`가 직접 추출하여 실행 검증합니다. 전체 validator에서도 호출하므로 C++17 컴파일러와 ASan/UBSan 지원이 필요합니다. 독립적으로 복사할 블록은 다른 블록에 대한 숨은 의존성을 두지 않습니다. 제출 소스에는 테스트 하네스의 헤더와 `main`을 넣지 않습니다.

공통 블록은 `python3 scripts/export_cpp_library.py --blocks array random --output /tmp/hc-common.cpp`처럼 본문에서 선택 추출합니다. 별도 복제 소스를 원문처럼 관리하지 않습니다. 풀이 레슨은 사용하는 블록 이름·입력 상한·작업 배열·초기화 시점을 적고 공통 구현을 다시 싣지 않습니다. 새 공통 기능은 실제 사용하는 레슨과 함께 추가합니다.

제출 입문 → ORDERING → 검증 → SA 흐름은 STL·표준 헤더·동적 할당 없이 유지합니다. 정렬·그리디·힙까지 전환한 본문은 `scripts/check_submission_examples.py`에서 금지 의존성과 헤더 없는 조합 컴파일, 실제 입력의 기준 답을 검사합니다. 일반 C++ 참고 예제를 일부 바꾼 것만으로 전체 기본 트랙이 전환됐다고 표시하지 않습니다.

ORDERING의 2-opt·난수·SA 블록 조합은 `python3 scripts/check_heuristic_search.py`로 검사합니다. 작은 지역 최적 반례, 모든 구간의 차분, 경계 입력, 최선해 보존과 재현성을 ASan/UBSan으로 확인합니다. 공개 채점기의 `main.cpp`를 보유한 경우 `--judge /path/to/main.cpp --output /tmp/ordering-bench.json`을 붙여 단계별 비용과 시간을 재현할 수 있습니다. 같은 후보 수와 같은 실행 시간은 서로 다른 비교 조건이므로 측정 기록에 구분해서 적습니다.

본문의 조합·경계·차분 사례는 `scripts/review-example-cases.json`에 추가하고 `python3 scripts/check_review_examples.py`로 실행합니다. 수정한 Markdown에서 코드를 직접 추출하며, 작은 독립 풀이와의 비교나 구체적인 실패 입력으로 설명과 구현을 함께 확인합니다. C++ 실행 검증 스크립트는 `-fno-sanitize-recover=all`을 사용하여 sanitizer 오류가 경고만 남기고 성공으로 끝나지 않도록 합니다.

문제 상황에서 시작해 작은 예시로 원리를 설명하고, 필요한 구현과 비용으로 이어갑니다. 모든 강의에 같은 목차를 맞추지 않습니다. 하위 페이지 목록을 썼다면 같은 링크를 나열하는 학습 순서를 다시 붙이지 않습니다.

예시는 새로운 풀이 판단, 상태 변화, 반례, 구현상의 차이 중 무엇을 설명하는지 분명해야 합니다. 이름만 나열한 응용, 한 줄 연산을 감싼 함수, 핵심 판정·전이를 비워 둔 프레임워크는 넣지 않습니다. 빠른 풀이와 기준 풀이가 같은 함수를 호출하는 비교 코드는 검증 예시가 아닙니다.

같은 구현을 부분 코드와 전체 코드로 반복하지 않습니다. 한 곳의 구현을 설명하고, 다른 레슨에서는 링크와 달라지는 조건만 둡니다. 대안 구현은 적용 조건이나 성능 차이를 설명할 때만 남깁니다. 삭제 후 독립적으로 읽을 내용이 부족한 페이지는 관련 본문에 합치고 manifest와 소개 문구를 맞춥니다.

조건과 주의점은 그 조건이 쓰이는 설명이나 코드 옆에 둡니다. 본문에서 설명한 내용을 결론, 실수 표, 체크리스트로 바꿔 반복하지 않습니다. 체크리스트는 검증 절차 자체를 가르치거나 서로 다른 조건을 실제로 비교해야 할 때만 사용합니다.

설명이 끝나면 그 자리에서 마칩니다. “핵심을 기억하자”, “문제 조건을 잘 확인하자”, “이 도구가 모든 문제의 정답은 아니다” 같은 일반론으로 결론 분량을 채우지 않습니다. 이어지는 문제가 있다면 문제를 먼저 소개하고 무엇을 구현하거나 비교할지 적습니다.

고급 레슨은 정의와 식만으로 끝내지 말고, 아래 중 최소 하나를 포함하는 것을 권장합니다.

- 손으로 따라갈 수 있는 작은 예시 또는 상태 변화 trace
- 왜 조건이 필요한지 보여 주는 반례
- 이 기법을 쓰지 말아야 하는 경우
- 좌표, 그래프, DP 상태 전이가 헷갈리는 주제의 간단한 도식

레슨 제목은 `lessons.json`의 `title`과 `lesson.md`의 H1이 정확히 같아야 합니다. 본문은 한국어 설명을 기본으로 하되, 통용되는 영어 용어는 처음 등장할 때 함께 적어도 됩니다.

h-contest 문제 링크를 넣을 때는 `/practice/<PROBLEM_ID>` 형식을 사용합니다. 운영 화면에서는 h-contest에 로그인한 사용자에게만 이 링크가 실제 문제 진입 링크로 활성화됩니다.

연습은 실제 문제 또는 입력·과제·확인 방법이 갖춰진 로컬 연습만 싣습니다. 본문 중간의 문제 링크, 짧은 문단, 목록도 사용할 수 있으며, 별도 연습 절이나 입문·표준·응용·함정 네 단계 표는 필수가 아닙니다. 관련성이 약한 문제를 분량을 채우기 위해 연결하지 않습니다.

입출력 예제를 자동 검산할 때는 `text exercise=<lessonId> role=input`과 `role=output` 코드 블록을 한 쌍으로 둡니다. `scripts/check_foundation_exercises.py`는 본문의 예제를 읽고 작은 독립 기준 풀이와 비교합니다. 이 검사는 예제의 정합성을 확인하며, 독자가 작성할 전체 제한용 풀이의 정확성까지 보장하지는 않습니다.

아직 준비하지 못한 연습과 본문 보강 항목은 [ROADMAP.md](ROADMAP.md)에 둡니다. 강의 본문에 `TODO` 행이나 빈 연습 페이지를 만들지 않습니다. `practiceStatus`는 실제 내용에 맞춰 `none`/`todo`/`linked`/`verified`로 표시하며, 예정 항목만 있는 강의를 `linked`로 표시하지 않습니다.

validator는 목차나 표 형식을 강제하지 않습니다. 기본·심화와 참고 노트의 모든 강의에서 본문의 `TODO`와 근거 없는 `linked`/`verified` 표시를 검사합니다. 미완성 연습 후보는 ROADMAP에 보관하고, 실제 연습이 없는 강의를 `linked`로 표시하지 않습니다.

C++ 코드 블록은 기본적으로 문법을 직접 확인합니다. 독립 translation unit으로 컴파일 가능한 예제는 fence에 `compile-check`를 붙이면 validator가 `c++ -std=c++17 -fsyntax-only`로 검사합니다.

````markdown
```cpp compile-check
long long square(int value) {
    return 1LL * value * value;
}
```
````

## 시각 자료와 단계별 데모

그림은 요약 문장을 장식하는 대신 입력·좌표·연결·상태 변화 중 무엇을 보여 주는지 먼저 정합니다. 넓은 SVG 안에 긴 설명을 작게 넣지 않고, 모바일 본문 폭에서도 읽을 수 있도록 짧은 라벨과 충분한 글자 크기를 씁니다. 전제와 긴 설명은 본문에 둡니다. 모든 SVG에는 `title`·`desc`와 구체적인 Markdown 대체 텍스트가 필요합니다.

진행 순서가 핵심인 예제는 `demos/`의 정적 HTML/CSS/classic JavaScript 데모를 사용합니다. 별도 라이브러리나 빌드 없이 실행되며, 모델은 `demos/models.js`에서 실제 상태를 계산합니다. 임의의 예시 슬라이드를 알고리즘 실행 결과처럼 표시하지 않습니다.

본문에는 다음과 같은 **단독 문단 링크**를 해당 설명 옆에 둡니다. GitHub/Pages에서는 독립 페이지로 열리고 h-contest 레슨 화면에서는 눌러 여는 데모로 표시됩니다.

```markdown
[이분 탐색: 답이 남는 구간 따라가기](https://blog.readiz.com/h-contest-lesson/demos/index.html?demo=binary-search)
```

등록 ID는 `binary-search`, `bfs`, `dijkstra`, `prefix-sum`, `two-opt`, `annealing`입니다. 새 ID를 추가하면 앱의 허용 목록도 같은 릴리즈에서 갱신해야 합니다. 공개 링크는 정확한 `https` URL과 `demo` 파라미터 하나만 사용합니다.

- 이전·다음·재생·처음·진행 위치와 관련 입력/예제를 제공하고 기본 자동재생은 끕니다. 입력 변경·마지막 단계·페이지 비활성화 시 재생을 멈춥니다.
- 작은 화면에서도 상태 설명과 수치는 HTML 텍스트로 읽을 수 있어야 합니다. 색상만으로 상태를 구분하지 않고 이름·테두리·기호를 함께 씁니다.
- 앱 iframe은 `sandbox="allow-scripts"`만 허용합니다. 외부 통신·저장소·부모 DOM 접근 없이 실행하고, 높이만 `hcontest-lesson-demo-resize` 메시지로 전달합니다.
- `node scripts/check_demos.cjs`로 독립 기준값·경계·중간 상태를 확인합니다. 전체 Python validator에도 포함되므로 Python/C++ 외 Node.js가 필요합니다.
- 390px·1280px 실제 브라우저에서 각 데모의 처음·중간·마지막 상태와 입력 변경, 키보드 조작, overflow를 확인합니다. 모델 검산만으로 시각 검수가 끝나지는 않습니다.
- 원본 Pages 공개 후 앱 저장소의 `node scripts/sync-lesson-demos.mjs ../h-contest-lesson`로 검증된 원본을 복사 배포합니다. 앱 복사본은 직접 수정하지 않습니다.

## PR 전에 확인할 것

- `lessons/<lessonId>/lesson.md`를 추가하거나 수정했나요?
- `lessons.json`의 title, description, summary, order, folderId, level, estimatedMinutes, prerequisites, nextLessons, relatedLessons, tags, pages를 갱신했나요?
- `python3 scripts/generate_catalog.py`를 실행했나요?
- `python3 scripts/validate_lessons.py`를 실행했나요?
- `lesson.md`의 H1 제목과 `lessons.json`의 title이 일치하나요?
- 이미지와 내부 링크가 깨지지 않나요?
- C++ 코드는 문법상 문제가 없나요?
- 미완성 연습은 본문 대신 `ROADMAP.md`에 남겼나요?
- 결론·체크리스트가 본문을 반복하거나 일반론으로 분량을 채우지 않나요?
- `lessonType`, `practiceStatus`, `implementationStatus`가 실제 문서 완성도와 맞나요?
- `difficultyAxes`가 레슨의 어려운 이유를 정확히 설명하나요?
- 새 허브나 트랙 역할이 생겼다면 생성 카탈로그의 빠른 길찾기와 트랙 지도도 맞게 갱신했나요?

공통 구현을 참조하는 예제는 의존 본문의 정의를 먼저 붙인다고 명시합니다. `scripts/review-example-cases.json`은 실제 Markdown 블록을 조합하고 `scripts/check_review_examples.py`로 경계·단순 풀이 비교를 실행합니다. 전체 validator에도 포함되어 있습니다. 전체 재검토 기록은 [LESSON_REVIEW.md](LESSON_REVIEW.md)에 남깁니다.
