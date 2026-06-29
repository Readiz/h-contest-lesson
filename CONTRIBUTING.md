# Contributing

h-contest-lesson 저장소는 h-contest 알고리즘 레슨 콘텐츠의 source of truth입니다.

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

아래 조건 중 둘 이상을 만족하면 `pages/` 분할을 우선 검토합니다.

- 본문이 공백 기준 약 800단어를 넘습니다.
- 핵심 하위 개념이 3개 이상입니다.
- 예시, 반례, 실수 포인트를 한 문서에 모두 넣으면 읽기 흐름이 끊깁니다.
- 상위 개념 허브로도 읽히고, 하위 특화 레슨으로도 읽히는 중첩 주제입니다.

분할할 때는 `lesson.md`에 개요, 읽는 순서, 문제 신호만 남기고 세부 증명, 구현 trace, 긴 예시는 `pages/*.md`로 옮깁니다.

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

`lessons.json`에는 새 레슨이 들어갈 `folderId`, `level`, `estimatedMinutes`, `prerequisites`, `nextLessons`, `relatedLessons`를 함께 지정합니다. 하위 페이지가 있으면 `pageId`, `title`, `description`, `order`, `file`을 가진 `pages` 배열을 추가합니다. 기존 폴더에 맞지 않는 주제라면 `folders` 배열에 새 폴더를 추가하고, `folderId`, `title`, `description`, `order`를 함께 작성합니다.

문서의 공개 성격이 명확하지 않으면 아래 metadata를 함께 지정합니다.

```json
{
  "status": "draft | review | published",
  "lessonType": "core | implementation | overview | reference | experimental",
  "seriesId": "parametric-optimization",
  "parentLessonId": "parametric-optimization",
  "practiceStatus": "none | todo | linked | verified",
  "implementationStatus": "concept-only | partial | full",
  "audience": "contest-core | advanced-contest | research-reference"
}
```

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

각 레슨은 가능하면 아래 흐름을 따릅니다.

1. 언제 이 개념이 필요한가
2. 핵심 아이디어
3. 작은 예시
4. C++ 구현
5. 시간 복잡도
6. 자주 하는 실수
7. 문제를 볼 때 체크할 조건
8. 대표 문제로 연결하기
9. 연습 문제

고급 레슨은 정의와 식만으로 끝내지 말고, 아래 중 최소 하나를 포함하는 것을 권장합니다.

- 손으로 따라갈 수 있는 작은 예시 또는 상태 변화 trace
- 왜 조건이 필요한지 보여 주는 반례
- 이 기법을 쓰지 말아야 하는 경우
- 좌표, 그래프, DP 상태 전이가 헷갈리는 주제의 간단한 도식

레슨 제목은 `lessons.json`의 `title`과 `lesson.md`의 H1이 정확히 같아야 합니다. 본문은 한국어 설명을 기본으로 하되, 통용되는 영어 용어는 처음 등장할 때 함께 적어도 됩니다.

h-contest 문제 링크를 넣을 때는 `/practice/<PROBLEM_ID>` 형식을 사용합니다. 운영 화면에서는 h-contest에 로그인한 사용자에게만 이 링크가 실제 문제 진입 링크로 활성화됩니다.

연습 문제 표는 아래 형식을 사용합니다. 아직 적절한 h-contest 문제가 없다면 문제 칸에 `TODO: ... /practice/... 문제 필요`를 남겨 빈칸을 명확히 드러냅니다.

```markdown
| 단계 | 문제 | 목표 | 힌트 키워드 |
| --- | --- | --- | --- |
| 입문 | TODO: /practice/... | 개념 그대로 적용 | ... |
| 표준 | TODO: /practice/... | 대표 구현 완성 | ... |
| 응용 | TODO: /practice/... | 다른 기법과 결합 | ... |
| 함정 | TODO: /practice/... | 자주 틀리는 조건 확인 | ... |
```

`TODO`는 practice 문제 매칭처럼 외부 운영 데이터가 아직 없는 곳에만 둡니다. 본문 설명, 정의, 코드, 복잡도, 경계 조건이 비어 있으면 공개 전 레슨 후보로 두고 [ROADMAP.md](ROADMAP.md)에 남깁니다.

모든 레슨 끝부분에는 가능하면 아래 세 블록을 같은 리듬으로 둡니다.

```markdown
## 문제를 볼 때 체크할 조건

## 구현 전 체크리스트

## 틀렸을 때 보는 체크리스트
```

기존 레슨의 표현이 이미 `문제에서 보이는 신호`, `자주 하는 실수`, `실전 체크리스트`처럼 다르게 잡혀 있다면 같은 의미를 유지해도 됩니다.

C++ 코드 블록은 기본적으로 문법을 직접 확인합니다. 독립 translation unit으로 컴파일 가능한 예제는 fence에 `compile-check`를 붙이면 validator가 `c++ -std=c++17 -fsyntax-only`로 검사합니다.

````markdown
```cpp compile-check
#include <bits/stdc++.h>
using namespace std;

int main() {
    return 0;
}
```
````

## PR 전에 확인할 것

- `lessons/<lessonId>/lesson.md`를 추가하거나 수정했나요?
- `lessons.json`의 title, description, summary, order, folderId, level, estimatedMinutes, prerequisites, nextLessons, relatedLessons, tags, pages를 갱신했나요?
- `python3 scripts/generate_catalog.py`를 실행했나요?
- `python3 scripts/validate_lessons.py`를 실행했나요?
- `lesson.md`의 H1 제목과 `lessons.json`의 title이 일치하나요?
- 이미지와 내부 링크가 깨지지 않나요?
- C++ 코드는 문법상 문제가 없나요?
- 적절한 h-contest 연습 문제가 없으면 `TODO`로 남겼나요?
- `lessonType`, `practiceStatus`, `implementationStatus`가 실제 문서 완성도와 맞나요?
- 새 허브나 트랙 역할이 생겼다면 생성 카탈로그의 빠른 길찾기와 트랙 지도도 맞게 갱신했나요?
