# Testing Strategy

Good tests aren't about coverage numbers — they're about confidence. A well-tested codebase
lets you refactor fearlessly and deploy on Friday.

## Test Design Decisions

### When to use table-driven tests

Use table-driven tests when:
- Same function, different inputs/outputs (the classic case)
- You're testing validation rules or parsing logic
- The test setup is identical across cases

```go
func TestParseAmount(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    int64
        wantErr bool
    }{
        {name: "valid cents", input: "1234", want: 1234},
        {name: "with decimal", input: "12.34", want: 1234},
        {name: "negative", input: "-5.00", want: -500},
        {name: "empty string", input: "", wantErr: true},
        {name: "not a number", input: "abc", wantErr: true},
        {name: "overflow", input: "99999999999999999999", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseAmount(tt.input)
            if tt.wantErr {
                assert.Error(t, err)
                return
            }
            assert.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### When NOT to use table-driven tests

Don't force everything into tables. Use standalone tests when:
- Each case needs significantly different setup
- The test tells a story (integration/scenario tests)
- You're testing complex interactions, not input/output pairs

```go
func TestOrderService_CreateOrder_DeductsInventory(t *testing.T) {
    // Arrange: specific setup for this scenario
    repo := &mockOrderRepo{}
    inventory := &mockInventory{available: 10}
    svc := order.NewService(repo, inventory)

    // Act
    _, err := svc.Create(ctx, order.CreateInput{
        ProductID: "prod-1",
        Quantity:  3,
    })

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, 7, inventory.available)
}
```

## Test Naming

Test names should read as behavior documentation. When a test fails, the name tells you
what broke without reading the code.

```
TestCreateOrder/when_product_is_out_of_stock_returns_error
TestCreateOrder/when_payment_fails_does_not_save_order
TestCreateOrder/when_successful_sends_confirmation_email
```

Pattern: `Test<Unit>/<when_condition>_<expected_behavior>`

## Mocking Strategy

### Mock at the interface boundary

Mock the dependencies of the thing you're testing, not the thing itself and not
deeper dependencies.

```go
// Testing OrderService — mock its dependencies (repo, notifier)
func TestOrderService_Create(t *testing.T) {
    mockRepo := &mockOrderRepo{
        saveFn: func(ctx context.Context, o *Order) error {
            return nil
        },
    }
    mockNotifier := &mockNotifier{}

    svc := order.NewService(mockRepo, mockNotifier)
    // test svc.Create(...)
}
```

### Function-based mocks vs struct-based mocks

For simple interfaces (1-2 methods), function-based mocks are cleaner:

```go
type mockRepo struct {
    findFn func(ctx context.Context, id string) (*Order, error)
    saveFn func(ctx context.Context, o *Order) error
}

func (m *mockRepo) FindByID(ctx context.Context, id string) (*Order, error) {
    return m.findFn(ctx, id)
}

func (m *mockRepo) Save(ctx context.Context, o *Order) error {
    return m.saveFn(ctx, o)
}
```

For complex interfaces or when the project uses testify/mock, use that framework consistently:

```go
type MockRepo struct {
    mock.Mock
}

func (m *MockRepo) FindByID(ctx context.Context, id string) (*Order, error) {
    args := m.Called(ctx, id)
    return args.Get(0).(*Order), args.Error(1)
}
```

### Mocks vs Fakes

- **Mock**: records calls, asserts expectations. Good for verifying interactions.
- **Fake**: working implementation with shortcuts (in-memory DB, local filesystem).
  Good for integration-like tests without external dependencies.

Use fakes when the behavior of the dependency matters to the test (e.g., "save then
retrieve should return the saved item"). Use mocks when you only care about the
interaction (e.g., "notifier was called with the right arguments").

## Test Helpers

Always mark test helpers with `t.Helper()`:

```go
func createTestOrder(t *testing.T, overrides ...func(*Order)) *Order {
    t.Helper()
    o := &Order{
        ID:        "test-order-1",
        Status:    StatusPending,
        CreatedAt: time.Now(),
    }
    for _, fn := range overrides {
        fn(o)
    }
    return o
}
```

`t.Helper()` ensures that when the test fails, the stack trace points to the test case,
not the helper function.

## Testing HTTP Handlers

Use `httptest.NewRecorder()` and `http.NewRequest()`:

```go
func TestGetOrder(t *testing.T) {
    svc := &mockOrderService{
        getOrderFn: func(ctx context.Context, id string) (*Order, error) {
            return &Order{ID: id, Status: "paid"}, nil
        },
    }
    handler := NewOrderHandler(svc)

    req := httptest.NewRequest(http.MethodGet, "/orders/123", nil)
    rec := httptest.NewRecorder()

    handler.GetOrder(rec, req)

    assert.Equal(t, http.StatusOK, rec.Code)

    var resp OrderResponse
    err := json.NewDecoder(rec.Body).Decode(&resp)
    assert.NoError(t, err)
    assert.Equal(t, "123", resp.ID)
}
```

## Running Tests

```bash
# All tests
go test ./...

# With race detector (always in CI)
go test -race ./...

# Single package
go test -v ./internal/usecases/createorder

# Single test
go test -v ./internal/usecases/createorder -run '^TestCreate$'

# Single subtest
go test -v ./internal/usecases/createorder -run 'TestCreate/when_valid'

# With coverage
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

## Test Organization

```
usecases/createorder/
├── usecase.go
├── usecase_test.go      # Unit tests for this use case
├── models.go
└── testdata/             # Test fixtures (JSON, golden files)
    ├── valid_input.json
    └── expected_output.golden
```

- Test files live next to the code they test
- `testdata/` is a Go convention — the toolchain ignores it
- Golden files for complex output validation (regenerate with a flag)
