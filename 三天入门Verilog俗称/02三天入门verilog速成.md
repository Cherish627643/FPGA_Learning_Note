# Verilog 入门第二天：always 语句块

## 1. always 语句块概述

**always 语句块**又称**过程块（procedural block）**，是 Verilog 中除 `assign` 之外另一种重要的赋值方式。

### 基本格式

```verilog
always @ (敏感信号条件表)
    各类顺序语句
```

### 核心特点

| 特点 | 说明 |
|------|------|
| 语句结构 | always 本身**不是单一有意义的语句**，必须与下方语句一起构成语句块（过程块） |
| 赋值名称 | 块内赋值称为**过程赋值语句** |
| 执行机制 | 块**不是始终处于激活状态**，满足敏感条件才执行，否则被**挂起** |
| 挂起行为 | 挂起时即使操作数变化也不执行赋值，赋值目标保持不变 |
| 赋值目标类型 | **必须是 `reg` 类型**（与 `assign` 的 `wire` 类型相对） |

> `assign` 语句中赋值目标是 `wire` 类型，`always` 语句中赋值目标必须是 `reg` 类型——这是两者的关键区别。

---

## 2. 激活条件（敏感信号条件表）

过程块由敏感信号条件表决定激活时机：

```verilog
// 边沿敏感（用于时序电路）
always @ (posedge clock)   // 时钟上升沿激活
always @ (negedge clock)   // 时钟下降沿激活

// 电平敏感（用于组合电路）
always @ (a, b, c)         // a、b、c 中任一变化即触发
always @ (a or b or c)     // 等效写法，用 or 分隔
```

### 边沿敏感关键字

- `posedge`：上升沿（positive edge），信号从 0 变 1
- `negedge`：下降沿（negative edge），信号从 1 变 0

---

## 3. assign 语句对比 always 语句

| 对比项 | `assign`（连续赋值） | `always`（过程赋值） |
|--------|---------------------|---------------------|
| 激活状态 | **始终处于激活状态** | 仅当敏感条件满足才激活 |
| 触发方式 | 操作数变化即计算和赋值 | 满足激活条件才计算和赋值 |
| 赋值目标类型 | `wire` 类型 | **`reg` 类型** |
| 能描述边沿变化 | ❌ 不能 | ✅ 能 |
| 可使用 if/case 等行为语句 | ❌ 不能 | ✅ 能 |

```verilog
// assign 例子
assign Q = D;   // D 变化马上计算和赋值，Q 必须是 wire

// always 例子
always @ (posedge clock)
    Q = D;      // 仅在 clock 上升沿才赋值，Q 必须是 reg
```

---

## 4. always 块中的 begin…end

**规则：如果 always 块中有多条赋值语句，必须用 `begin…end` 括起来。**

```verilog
// 单条语句可省略 begin…end
always @ (a)
    c = a;

// 多条语句必须加 begin…end
always @ (a or b or c)
    begin
        s = ...;
        c_out = ...;
    end
```

> 建议养成良好编码风格，always 块中都加上 `begin…end`。

### begin…end 内的执行顺序

- Verilog 语言中，**所有语句默认是并行执行的**
- 只有 **`begin…end` 内部的语句才是顺序执行**的

---

## 5. D 触发器实例（综合应用）

```verilog
module DFF2(clock, D, Q, reset, EN);
    input clock, D, reset, EN;
    output Q;
    reg Q;

    always @ (posedge clock or negedge reset)
        begin
            if (!reset)          // reset 为 0（低电平有效）时复位
                Q = 0;
            else if (EN)         // 使能有效时采样 D
                Q = D;
        end
endmodule
```

**逻辑说明：**
- `posedge clock` 或 `negedge reset` 任一发生即进入过程块
- `reset` 为 0 时执行复位（`Q = 0`）
- 否则判断 `EN`，为 1 时把 D 赋给 Q
- 这就是一个标准的 D 触发器（D Flip-Flop）

---

## 6. 阻塞赋值与非阻塞赋值

这是 Verilog 中**最重要也最容易出错**的知识点。

### 阻塞赋值 `=`（blocking）
- 顺序立即执行：算一条，赋值一条
- 常用于**组合电路**设计

### 非阻塞赋值 `<=`（non-blocking）
- 全部先计算右边，等所有语句右值算完后再统一赋值
- 常用于**时序电路**设计

### 关键原则

> ⚠️ **绝对禁止**在一个 always 块中混合使用阻塞赋值和非阻塞赋值。

| 场景 | 推荐的赋值方式 |
|------|---------------|
| 设计组合电路 | 阻塞赋值 `=` |
| 设计时序电路 | 非阻塞赋值 `<=` |

小模块时混用可能不报错，但综合大模块时容易出错，因为 Verilog 只是描述电路而非完全等同实际电路。

---

## 7. 阻塞赋值实现组合电路（全加器片段）

```verilog
module my_adder(A, B, Cin, Sum, Cout);
    input A, B, Cin;
    output Sum, Cout;
    reg Sum, Cout;
    reg M;

    always @ (A or B or Cin)
        begin
            M = B | Cin;
            Sum = A ^ M;
            Cout = A & M;
        end
endmodule
```

**执行过程分析：**
1. **先统一计算所有等号右边的值**
   - `M` = `B | Cin` = `1 | 0` = `1`
   - `Sum` = `A ^ M` = `1 ^ 1` = `0`
   - `Cout` = `A & M` = `1 & 1` = `1`
2. **再统一赋值**

中间变量 `M`（在 input/output 中未声明，仅作为内部变量）使电路描述更清晰。

---

## 8. 非阻塞赋值实现时序电路（一级寄存器 / 打一拍）

```verilog
module DFF3(clock, D, Q);
    input clock, D;
    output Q;
    reg A, B;

    always @ (posedge clock)
        begin
            A <= D;    // D 的值赋给 A
            B <= A;    // A 的旧值赋给 B
            Q <= B;    // B 的旧值赋给 Q
        end
endmodule
```

### 工作机制（打两拍）

由于非阻塞赋值是**先全部计算右值、再统一赋值**：

| 时钟周期 | A | B | Q |
|----------|---|---|---|
| 初始 | 0 | 0 | 0 |
| 上升沿 1 | D 的值 | A 的旧值（0） | B 的旧值（0） |
| 上升沿 2 | … | … | A 的旧值 |

→ **D 经过两个时钟周期才到达 Q**，称为"打了两拍"。

> 这种打拍方式在后续学习**亚稳态（metastability）消除**时至关重要，比如常见的"两级触发器同步器"。

---

## 9. 四位二进制加法计数器

```verilog
module count4(clock, Q);
    input clock;
    output [3:0] Q;       // Q 是 4 位宽的数
    reg [3:0] Q;
    reg [3:0] Q1;         // 内部中间变量

    always @ (posedge clock)
        begin
            Q1 = Q + 1;
            Q  = Q1;
        end
endmodule
```

**功能：** 每当时钟上升沿到来，Q 加 1（自增）。

**说明：**
- `output [3:0] Q`：声明 Q 为 4 位宽输出
- 内部信号 `Q1` 是中间变量，需在使用前声明
- 内部信号声明格式：`数据类型 位宽 信号名称 [元素个数]`
- `always` 与 `assign`（若有）语句之间是**并行**执行的
- 没有 `Q1` 的写法：`Q = Q + 1;`（可直接这样写）

---

## 10. 底层模块的调用（模块实例化）

### 设计思路

设计复杂电路时，可先做底层模块（如 D 触发器），再在顶层模块中调用。

### 底层模块：D 触发器

```verilog
module DFF(clock, D, Q);
    input clock, D;
    output Q;
    reg Q;

    always @ (posedge clock)
        Q = D;
endmodule
```

### 顶层模块：调用两个 DFF

```verilog
module exam(clock, D, Q);
    input clock, D;
    output Q;
    wire D1, Q1;      // 内部连线变量

    // 实例化第一个 DFF
    DFF DFF1(
        .clock(clock),
        .D(D),
        .Q(Q1)
    );

    // 实例化第二个 DFF
    DFF DFF2(
        .clock(clock),
        .D(D1),         // 此处应接到第一级输出，示例略
        .Q(Q)
    );
endmodule
```

### 实例化格式

```verilog
模块名 实例化名(端口映射);
```

- **实例化名不能省略**
- 实例化名可任意（如 `DFF1`、`DFF2`、`abc` 都可），但应避免与端口名冲突
- 顶层模块中需声明内部连线变量（如 `D1`、`Q1`）

### 端口映射的两种方法

#### ① 端口名关联法（推荐）

```verilog
.底层端口名(外部信号)
```

格式清晰，**不必按底层模块端口顺序写**。

```verilog
DFF DFF1(
    .clock(clock),
    .D(D),
    .Q(Q1)
);
```

> 最后一个端口映射后**不加逗号**。

#### ② 位置关联法（不推荐）

按底层模块端口列表的顺序逐个传入，代码可读性差，应避免使用。

---

## 11. Verilog 内置门原语（Gate Primitives）

Verilog 提供 12 个内置门原语，无需功能描述即可直接调用。

**常见门原语：**

| 门原语 | 名称 |
|--------|------|
| `and` | 与门 |
| `or` | 或门 |
| `not` | 非门 |
| `nand` | 与非门 |
| `nor` | 或非门 |
| `xor` | 异或门 |
| `xnor` | 同或门 |

### 调用语法

```verilog
门原语 实例名(输出, 输入1, 输入2, ...);
```

- **实例名可省略**
- 与模块调用不同，门原语的端口连接**只采用顺序法**
- **输出在前，输入在后**

```verilog
// 例子：两输入与门
and my_and(out, a, b);    // out = a & b
```

> 实际设计中门原语使用频率较低，了解即可。

---

## 12. 关键术语速查表

| 术语 | 原文 | 含义 |
|------|------|------|
| 过程块 | Procedural Block | 即 always 语句块 |
| 过程赋值 | Procedural Assignment | always 块内的赋值 |
| 阻塞赋值 | Blocking Assignment | `=`，立即执行 |
| 非阻塞赋值 | Non-blocking Assignment | `<=`，统一赋值 |
| 上升沿 | Positive Edge (`posedge`) | 信号 0→1 |
| 下降沿 | Negative Edge (`negedge`) | 信号 1→0 |
| 边沿敏感 | Edge-sensitive | 沿触发 |
| 实例化 | Instantiation | 调用子模块 |
| 门原语 | Gate Primitive | Verilog 内建基本门 |
| 亚稳态 | Metastability | 触发器采样违例的中间态，需多级打拍消除 |