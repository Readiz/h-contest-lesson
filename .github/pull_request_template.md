## 변경 내용

-

## 변경 종류

- [ ] 오탈자/표현 수정
- [ ] 기존 레슨 설명 보강
- [ ] 코드 예제 수정
- [ ] 이미지/링크 수정
- [ ] 새 레슨 추가
- [ ] 기타

## 체크리스트

공통:

- [ ] 수정한 문장이 기존 레슨 문체와 잘 맞습니다.
- [ ] 이미지와 내부 링크가 깨지지 않습니다.
- [ ] C++ 코드 예제의 문법을 확인했습니다.
- [ ] 이미 공개된 레슨 이동/보강 기록은 `CHANGELOG.md`, 미공개 후보와 practice TODO는 `ROADMAP.md`에 남겼습니다.

새 레슨 추가 시:

- [ ] `lessons/<lessonId>/lesson.md`를 추가하거나 수정했습니다.
- [ ] 긴 레슨은 `lesson.md` 허브와 `pages/*.md` 분할 기준을 검토했습니다.
- [ ] `lessons.json`의 title, description, summary, order, folderId, level, estimatedMinutes, prerequisites, nextLessons, relatedLessons, tags를 갱신했습니다.
- [ ] `python3 scripts/generate_catalog.py`를 실행했습니다.
- [ ] `python3 scripts/validate_lessons.py`를 실행했습니다.
- [ ] `lesson.md`의 H1 제목과 `lessons.json`의 title이 일치합니다.
- [ ] 이미지와 내부 링크가 깨지지 않습니다.
- [ ] C++ 코드 예제의 문법을 확인했습니다.
- [ ] 고급 레슨에는 작은 예시, 반례, 구현 trace, 또는 쓰지 말아야 할 경우 중 하나 이상을 넣었습니다.
- [ ] 적절한 practice 문제가 없으면 임의 ID 대신 `TODO: /practice/... 문제 필요`로 남겼습니다.

## 관련 Issue

Closes #
