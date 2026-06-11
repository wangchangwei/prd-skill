# Task Breakdown Fallback：当 superpowers 不可用时的任务拆解模板

> 用于 prd-writer 阶段 3.6。当环境未安装 `superpowers:writing-plans` 时，按本文件模板产出 `<产物目录>/task-breakdown.md`。

## 核心原则（来自 writing-plans）

1. **bite-sized**：每步 2-5 分钟（不是"做完一个模块"）
2. **零上下文**：写给"对这个项目一无所知的工程师"
3. **完整代码**：每步含完整代码块（严禁"TBD" / "see Task N" / "add appropriate handling"）
4. **exact 路径**：每个文件路径都是 git 仓库真实位置
5. **每步可验证**：运行命令 + 预期输出
6. **频繁 commit**：每个任务完成就 commit

## 反 placeholder 清单

**绝不能出现**：
- "TBD" / "TODO" / "implement later" / "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above"（不写具体测试代码）
- "Similar to Task N"（直接重复代码，不让工程师跨任务读）
- 没有代码块的"如何做"步骤

---

## 模板 A：TDD 流（适合有单元测试的代码：service / lib / 后端）

````markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [一句话写清要构建什么]

**Architecture:** [2-3 句讲总体方案]

**Tech Stack:** [关键依赖 / 库]

---

### Task 1: [组件名]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

---

## 模板 B（非 TDD 流 / 备选）：适合原型 / UI / 无测试的产物

````markdown
### Task N: [组件名]

**Files:**
- Create: `exact/path/to/file.html`
- Modify: `exact/path/to/existing.css:80-110`

- [ ] **Step 1: Create the file with full content**

```html
<!DOCTYPE html>
<html>
  <body>...</body>
</html>
```

- [ ] **Step 2: Manually verify in browser**

Run: open `file:///<abspath>/file.html` in browser
Expected: 看到 [具体视觉描述]

- [ ] **Step 3: Commit**

```bash
git add file.html
git commit -m "feat: add specific feature"
```
````

---

## 任务示例

### Task 1: 添加"上次同款"加购接口

**Files:**
- Create: `src/api/reorder.ts:0`
- Modify: `src/api/orders.ts:42-58`
- Test: `tests/api/reorder.test.ts:0`

- [ ] **Step 1: Write the failing test**

```typescript
describe('POST /api/reorder', () => {
  it('rejects unknown openid', async () => {
    const res = await request(app).post('/api/reorder').send({ openid: 'ghost' });
    expect(res.status).toBe(404);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest tests/api/reorder.test.ts -v`
Expected: FAIL "Cannot find module"

- [ ] **Step 3: Write minimal implementation**

```typescript
router.post('/api/reorder', async (req, res) => {
  const last = await db.orders.findOne({ openid: req.body.openid, status: 'completed' }).sort({ createdAt: -1 });
  if (!last) return res.status(404).end();
  res.json(last.items);
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest tests/api/reorder.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/api/reorder.ts tests/api/reorder.test.ts
git commit -m "feat: add reorder API returning last completed order items"
```

---

## 内联 3 项 Self-Review（来自 writing-plans skill）

> 写完 task-breakdown.md 后，自己过一遍：

### 1. Spec 覆盖（必须）
- [ ] 打开 PRD 的 5.x 节 / Feature List 的每个 M-XX
- [ ] 每个 P0 功能都至少有一个 Task 覆盖
- [ ] 每个 N-XX 非功能要求都有对应 Task

### 2. Placeholder 扫描
- [ ] grep -n "TBD\|TODO\|see Task\|Similar to\|add appropriate\|implement later" task-breakdown.md
- [ ] 0 命中（或每个命中都有解释）

### 3. 类型一致性
- [ ] 函数名 / 方法签名 / 属性名在所有 Task 中一致
- [ ] 任何 Task 3 引入的类型在 Task 5 用到时必须先确保 Task 4 已导入

如果发现问题，**直接 inline 修复**，不用重新 review。
