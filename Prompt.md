使用serena工具对项目的测试代码进行全面盘点，输出基线摸底报告。

## 扫描范围
1. 识别项目中所有的测试相关目录（常见名称：tests/、test/、unittest/、*_test/）
2. 识别所有测试文件（命名符合 test_*.py、*_test.py 等pytest约定的文件）

## 对每个测试目录，统计
- 测试文件数量
- 测试函数总数（def test_*开头的函数）
- 测试类数量（class Test*开头的类）
- 使用的pytest高级特性：
  - fixture数量和名称
  - conftest.py的存在和内容概要
  - 使用的mark装饰器（@pytest.mark.*）
  - 参数化测试的使用情况（@pytest.mark.parametrize）
  
## 对每个测试文件，简要分析
- 测试目标（从文件名和内容推断，如 test_tensor.py 对应 snnx_tensor API）
- 测试函数数量
- 是否有文件级fixture或setup
- 是否有skip/xfail等跳过的测试，统计数量和原因

## 输出格式
保存到 docs/baseline_test_inventory.md，包含：

1. 总览数字（文件数、测试数、fixture数）
2. 按目录的统计表
3. 按测试目标的统计表
4. pytest特性使用频率统计
5. 观察到的组织模式（比如 "测试按API对象组织"、"每个文件一个conftest"）

## 注意事项
- 不要遗漏任何测试目录，包括子目录
- 只统计，不评价质量（质量分析是下一步的任务）
- 如果发现有example或demo代码被放在tests目录但不是真正的测试，单独标注









使用serena工具，将项目的已有测试与pybind API清单对应起来，分析测试覆盖情况。

## 前置输入
- API清单：docs/pybind_api_list.md（或你改名后的文件名）
- 测试存量：docs/baseline_test_inventory.md

## 分析任务

### 1. 测试-API 映射
对每个测试文件/测试函数，识别它实际测试的pybind API是哪些。方法：
- 扫描测试代码中的import语句
- 扫描测试代码中被调用的API（通过find_referencing_symbols反向查找）
- 综合判断该测试覆盖了哪些API

### 2. API覆盖统计
对pybind API清单中的每个API，标注：
- 是否有专门的测试（函数名明确对应，如 test_insert_layer 对应 insert_layer）
- 是否有间接测试（在其他测试中被调用，但不是主测试目标）
- 完全未覆盖（既没专门测试也没被间接调用）

### 3. 覆盖维度分析
对有测试的API，分析它的测试覆盖了哪些维度：
- Happy path（正常输入）
- 边界值（空输入、极值等）
- 异常处理（非法输入）
- 不变量验证（操作后状态正确）

判断依据：看测试函数名（如 test_xxx_empty、test_xxx_invalid）和断言模式。

## 输出格式
保存到 docs/baseline_test_coverage.md，包含：

1. 整体覆盖率概要
   - 总API数 / 有专门测试的API数 / 有任何形式测试的API数 / 完全未覆盖的API数
   - 百分比
2. 按API分类的覆盖表
   - 分类（query/mutation/io等）× 覆盖状态 的矩阵
3. 完全未覆盖API清单（按测试优先级排序）
4. 覆盖深度分析
   - 多少API有happy path测试
   - 多少API有边界测试
   - 多少API有异常测试
   - 多少API有完整四维覆盖

## 注意事项
- 这个分析不涉及代码coverage工具（line/branch coverage），只看"哪些API有对应测试"
- 对于pybind包装的API，要区分"测试Python侧包装"还是"测试C++侧逻辑"
- 如果遇到判断困难的case，列在"存疑清单"里供人工review















使用serena工具对项目已有测试进行质量画像分析，为后续AI生成测试的质量评估建立基线。

## 分析维度

### 1. 断言强度分析
随机抽样30个测试函数（或全部，如果总数小于30），分析：
- 平均每个测试的断言数
- 断言类型分布：
  - 精确值断言（assert x == 5）
  - 范围断言（assert x > 0）
  - 类型断言（assert isinstance(x, Tensor)）
  - 存在性断言（assert x is not None）
  - 异常断言（pytest.raises）
- 弱断言比例（只有 is not None 或 True/False 这类）

### 2. 测试结构特征
- Arrange-Act-Assert模式的使用情况
- fixture的复用程度
- parametrize参数化的使用情况（测试多少个case用参数化实现）
- setup/teardown的处理方式

### 3. 命名规范
- 测试函数命名风格（test_feature_scenario / test_behavior / 混合）
- 命名一致性（同一个API的不同测试是否命名连贯）
- 语义化程度（看名字能否猜出测什么）

### 4. 覆盖深度
- 边界值测试的典型模式（空输入怎么测、极值怎么测）
- 异常测试的完整性（是否验证异常类型和消息）
- 不变量测试的存在情况

### 5. 可维护性
- 魔法数字的使用频率
- 测试间的依赖关系（有没有test_b依赖test_a跑完）
- 注释质量

### 6. 值得AI学习的模式
列出5-10个"模范测试"，这些测试可以作为few-shot样例。挑选标准：
- 结构清晰
- 断言有力
- 覆盖维度全
- 注释恰当
- 复用了fixture等高级特性

## 输出格式
保存到 docs/baseline_test_quality.md，包含：

1. 质量指标汇总表（数值 + 百分比）
2. 典型优秀测试样例（至少5个，给出文件路径和行号，简要说明好在哪）
3. 典型待改进测试样例（至少3个，说明问题在哪，仅用于内部参考，不公开批评）
4. 值得沉淀为prompt约束的团队模式
   例如："团队习惯用XXX fixture做setup"、"异常测试必须验证exception message"
5. 质量基线数据（供后续AI生成测试对比）

## 注意事项
- 分析基于静态代码，不执行测试
- 评价要客观，基于代码事实，不做主观好坏判断
- "待改进"样例要注意措辞，目的是识别模式，不是批判作者
- 特别关注pytest高级特性（fixture、parametrize、mark）的使用，这些是AI最容易漏学的

