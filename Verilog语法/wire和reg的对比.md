# 大方向对比
Q：wire理解为导线本身不储存数值，reg可以记录数值

你的理解**大方向对，但要加一句关键限定**：

> **wire 是“连线”，不存储；reg 是“过程赋值变量”，仿真中能保持值，但不一定综合成寄存器。**  
> 在 Verilog 里，**reg ≠ register**，看到 `reg` 不要立刻认为它是触发器。

## 对比表

| 项目 | wire | reg |
|---|---|---|
| 本质 | 线网 net，表示连接 | 变量 variable，过程赋值目标 |
| 赋值方式 | `assign`、模块端口、门原语 | `always` / `initial` 过程块 |
| 仿真行为 | 由驱动源决定，无驱动为 `z` | 保持最后一次过程赋值，未赋值常为 `x` |
| 是否存储 | 不存储 | 类型本身不保证，看综合上下文 |
| 综合结果 | 连线、组合逻辑输出 | 可能是组合逻辑，也可能是触发器/锁存器 |
| 典型端口 | `input` 默认是 wire | `output reg` 需过程赋值时用 |
| 多驱动 | 可多驱动，靠 net 解析 | 通常不允许 |
| 读代码时看 | 谁在驱动它 | 它在哪种 `always` 里 |

## 关键：reg 综合成什么，取决于 always

### 1. wire + assign：组合逻辑连线

```verilog
wire y;
assign y = a & b;
```

`y` 是一根线，由与门输出驱动，输入一变，`y` 就变。

### 2. reg + always @(*)：还是组合逻辑

```verilog
reg y;
always @(*) begin
    y = a & b;
end
```

虽然写的是 `reg`，但综合出来通常还是与门，不是寄存器。  
因为 `always @(*)` 对输入敏感，输入变了就重新计算。

### 3. reg + always @(posedge clk)：这才是触发器

```verilog
reg q;
always @(posedge clk) begin
    q <= d;
end
```

这个 `q` 才通常综合成 D 触发器，在时钟上升沿更新，并保持到下一个上升沿。

## 所以更准确的说法是

- `wire`：**结构连线**，必须被驱动，不存储。
- `reg`：**过程赋值变量**，仿真中能保存值；硬件上可能是：
  - 组合逻辑输出；
  - 锁存器；
  - 触发器；
  - 取决于 `always` 的敏感列表和赋值是否完整。

## 一个例子对比

```verilog
module demo(
    input clk,
    input a, b,
    output wire y,
    output reg z,
    output reg q
);

    assign y = a & b;          // wire：组合逻辑

    always @(*) begin
        z = a & b;             // reg：但综合成组合逻辑
    end

    always @(posedge clk) begin
        q <= a & b;            // reg：综合成触发器
    end

endmodule
```

这里：

- `y` 是 wire，组合输出；
- `z` 是 reg，但也是组合输出；
- `q` 是 reg，且是时序逻辑，通常对应触发器。

## 总结口诀

> **wire 看驱动，reg 看 always。**  
> **wire 是线，reg 是过程变量；reg 不一定寄存器。**

读 Verilog 时，不要只盯着 `wire` 和 `reg` 这两个关键字，而要看：

1. 它在哪里被赋值？
2. 是连续赋值还是过程赋值？
3. 敏感列表是 `*` 还是 `posedge clk`？
4. 赋值完整不完整？
5. 综合出来是连线、组合逻辑，还是触发器？

这样就不会被 `reg` 这个名字误导。


# 何时用wire，何时用reg

最实用的判断法不是“它存不存储”，而是：

> **它在哪儿被赋值？谁在驱动它？**

Verilog-2001 里，语法规则其实很硬：

- `assign` 左边 → 必须是 `wire`
- `always` / `initial` 左边 → 必须是 `reg`
- 模块实例化输出、门原语输出、双向口 → 连 `wire`
- `output` 端口看内部怎么驱动：`assign` 驱动用 `output wire`，`always` 驱动用 `output reg`
- `input` 端口默认 `wire`
- `inout` 必须 `wire`

## 快速对照表

| 场景 | 用 wire 还是 reg |
|---|---|
| `assign y = a & b;` | `wire y;` |
| `always @(*) y = a & b;` | `reg y;` |
| `always @(posedge clk) q <= d;` | `reg q;` |
| 模块例化输出连接 | `wire out;` |
| 门原语输出 | `wire` |
| 双向端口 `inout` | `wire` |
| 测试平台里产生时钟、复位、激励 | `reg` |
| DUT 输出连到 testbench | `wire` |
| `output` 由 `assign` 驱动 | `output wire` |
| `output` 由 `always` 驱动 | `output reg` |

## 例子

### 1. 组合逻辑两种写法

用 `assign`：

```verilog
wire y;
assign y = a & b;
```

用 `always`：

```verilog
reg y;
always @(*) begin
    y = a & b;
end
```

虽然第二个写的是 `reg`，但综合出来通常还是组合逻辑，不是触发器。  
因为它不在时钟边沿更新。

### 2. 时序逻辑

```verilog
reg q;
always @(posedge clk) begin
    q <= d;
end
```

这里 `q` 是 `reg`，通常综合成 D 触发器。

### 3. 模块输出端口

```verilog
module demo(
    input clk,
    input a,
    input b,
    output wire y,
    output reg q
);

    assign y = a & b;

    always @(posedge clk) begin
        q <= a & b;
    end

endmodule
```

- `y` 由 `assign` 驱动 → `output wire`
- `q` 由 `always` 驱动 → `output reg`

### 4. 模块实例化

```verilog
wire out;
sub u_sub(
    .out(out),
    .in(a)
);
```

模块输出是驱动源，所以连到 `wire`。

### 5. Testbench

```verilog
reg clk;
reg rst;
wire dout;

initial begin
    clk = 0;
    forever #5 clk = ~clk;
end

initial begin
    rst = 1;
    #20 rst = 0;
end

dut u_dut(
    .clk(clk),
    .rst(rst),
    .dout(dout)
);
```

- `clk`、`rst` 在 `initial/always` 里赋值 → `reg`
- `dout` 是 DUT 输出 → `wire`

## 常见错误

```verilog
wire y;
always @(*) y = a & b;   // 错：wire 不能出现在过程赋值左边

reg q;
assign q = a & b;        // 错：reg 不能用于连续赋值左边
```

## SystemVerilog 里的 `logic`

SystemVerilog 引入了 `logic`，大部分场景可以替代 `wire` 和 `reg`：

```verilog
logic y;
assign y = a & b;        // 可以

logic q;
always @(posedge clk)
    q <= d;              // 可以
```

但注意：

- **多驱动**、双向总线仍然要用 `wire`。
- 单驱动时 `logic` 很方便，但不要因为用 `logic` 就忘了硬件本质。

## 判断口诀

> **always 左值用 reg，assign 左值用 wire；**  
> **模块输出连 wire，双向端口必须 wire；**  
> **output 看驱动：assign 用 wire，always 用 reg；**  
> **SystemVerilog 用 logic，多驱动还得 wire。**

所以，写代码时先问自己：

1. 这个信号在 `always/initial` 里被赋值吗？是 → `reg` / `logic`。
2. 它由 `assign`、模块输出、门原语驱动吗？是 → `wire`。
3. 它是端口吗？`input` → `wire`；`output` 看内部驱动；`inout` → `wire`。
4. 有多个驱动源吗？有 → `wire`。

记住：**`reg` 不等于寄存器，`wire` 不等于简单连线。关键看赋值方式和驱动来源。**

