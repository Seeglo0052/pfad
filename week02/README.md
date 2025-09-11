# ?? 潮汐数据可视化项目 / Tides Data Visualization Project

这是一个全面的潮汐数据收集、处理和可视化项目，提供多种动态和交互式的数据展示方式。

## ?? 项目特性

- **数据收集**: 自动从香港天文台获取潮汐数据
- **数据处理**: 清理、验证和结构化潮汐数据
- **静态可视化**: 创建传统图表和分布图
- **动画效果**: 生成流动的波浪动画GIF
- **交互式仪表板**: 基于Plotly的Web仪表板
- **艺术效果**: SVG动画和创意可视化
- **圆形可视化**: 极坐标潮汐图表

## ?? 项目结构

```
week02/
├── ?? 数据文件
│   ├── tides.csv                      # 潮汐数据CSV文件
│   └── .env                           # 环境配置文件
├── ?? Python脚本
│   ├── run_all.py                     # ?? 主运行脚本 (从这里开始!)
│   ├── plot_tides.py                  # 数据收集和基础可视化
│   ├── enhanced_tides_visualization.py # 增强可视化功能
│   ├── draw_svg.py                    # SVG艺术效果创建
│   ├── tides_csv.py                   # 原始CSV生成器
│   ├── scraping_utils.py              # 网页抓取工具
│   └── multi_city_temp.py             # 多城市温度数据
├── ?? 配置文件
│   └── requirements.txt               # Python依赖包列表
└── ?? 输出文件 (运行后生成)
    ├── tides_basic_plot.png           # 基础图表
    ├── tides_animation.gif            # 动画波浪
    ├── interactive_tides.html         # 交互式仪表板
    ├── circular_tides.png             # 圆形潮汐图
    ├── flowing_tides.svg              # SVG流动效果
    ├── flowing_tides_enhanced.svg     # 增强SVG动画
    └── tide_clock.svg                 # 潮汐时钟
```

## ?? 快速开始

### 方法1: 一键运行 (推荐)

```bash
# 运行主脚本，它会自动处理一切
python run_all.py
```

### 方法2: 逐步运行

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **收集数据并创建基础可视化**
```bash
python plot_tides.py
```

3. **创建增强可视化效果**
```bash
python enhanced_tides_visualization.py
```

4. **创建SVG艺术效果**
```bash
python draw_svg.py
```

## ?? 依赖包

项目需要以下Python包：

- `python-dotenv`: 环境变量管理
- `requests`: HTTP请求
- `lxml`: HTML/XML解析
- `matplotlib`: 基础图表绘制
- `pandas`: 数据处理
- `numpy`: 数值计算
- `seaborn`: 统计可视化
- `plotly`: 交互式图表
- `drawsvg`: SVG图形创建

## ?? 生成的可视化效果

### 1. 基础潮汐图表 (`tides_basic_plot.png`)
- 时间序列线图
- 移动平均趋势
- 潮汐高度分布直方图

### 2. 动画波浪效果 (`tides_animation.gif`)
- 流动的波浪动画
- 粒子效果
- 实时数据反映

### 3. 交互式仪表板 (`interactive_tides.html`)
- 多面板仪表板
- 可缩放的时间序列
- 热力图和3D表面图
- 交互式图例

### 4. 圆形潮汐图 (`circular_tides.png`)
- 极坐标展示
- 多层圆形可视化
- 颜色映射潮汐高度

### 5. SVG艺术效果
- `flowing_tides_enhanced.svg`: 流动波浪艺术
- `tide_clock.svg`: 潮汐时钟设计
- 矢量图形，无限缩放

## ?? 配置选项

编辑 `.env` 文件来自定义数据源：

```env
YEAR=2023                                           # 数据年份
URL='https://www.hko.gov.hk/tide/eCLKtext${YEAR}.html'  # 数据源URL
ROW_XPATH="//html/body/table/tbody/tr"             # 表格行选择器
COL_XPATH="td"                                      # 表格列选择器
```

## ?? 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 使用国内镜像源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **数据获取失败**
   - 检查网络连接
   - 验证.env文件中的URL
   - 确认香港天文台网站可访问

3. **动画生成慢**
   - 动画包含大量帧，生成需要时间
   - 可以在代码中调整frames参数

4. **SVG文件无法打开**
   - 使用现代浏览器打开SVG文件
   - 或使用支持SVG的图像查看器

## ?? 数据说明

- **数据源**: 香港天文台官方潮汐数据
- **数据格式**: 日期时间 + 潮汐高度(米)
- **更新频率**: 每6小时一次观测
- **数据精度**: 厘米级精度

## ?? 使用建议

1. **首次运行**: 使用 `python run_all.py` 获得完整体验
2. **数据分析**: 查看 `interactive_tides.html` 进行深入分析
3. **演示展示**: 使用动画GIF和SVG文件进行展示
4. **自定义开发**: 基于现有代码模块进行二次开发

## ?? 项目改进

相比原始版本，此项目进行了以下改进：

1. **错误处理**: 添加了完善的异常处理机制
2. **代码结构**: 采用面向对象设计，模块化开发
3. **数据验证**: 增加数据清洗和验证步骤
4. **可视化增强**: 多种图表类型和动画效果
5. **用户体验**: 一键运行和自动依赖检查
6. **文档完善**: 详细的使用说明和故障排除

## ?? 许可证

本项目仅用于学习和研究目的。数据来源于香港天文台公开数据。

---

?? 享受潮汐数据的美妙可视化之旅！ ??