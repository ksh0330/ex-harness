# 가상 과제 README: 지역 자료 보관 CSV 연계

연습용 합성 업무다. 기존 `examples/batch.py`와 `examples/data/archive.csv`가 출발점이다.
새 공급자는 다음 CSV를 보낸다.

```csv
name,stage
Village interview,pending
Old festival film,processing
Poster scan,complete
```

현재 가져오기가 실패한다. 업무 담당자는 “pending도 미처리 자료인데 전부 실패해서 불편하다”고 한다.
기존 queued 입력·잘못된 행의 전체 거부·기존 데이터 보존은 유지해야 한다.
외부 API·UI·새 DB·개인정보를 추가하지 않는다. PM이 호환 범위와 중복 정책을 결정한다.

## 필수 확인

1. 실패를 실제 CLI와 관련 테스트로 재현한다.
2. 어떤 입력을 허용하고 무엇을 거부할지 PM이 결정한다.
3. 결정한 범위만 수정하고 새 입력·기존 입력·오류 원자성을 검증한다.
4. 가져오기 후 JSON 보고서로 레코드·상태 집계를 확인한다.

행 수·소요 시간·절감률은 측정하지 않았다. 테스트 fixture의 숫자를 실제 업무 성과로 사용하지 않는다.
