"""
Flask CLI 命令扩展
数据管理相关命令（与 Flask-Migrate 兼容）
"""
import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import TestSuite, TestCase, TestPlan


@click.command('seed-data')
@with_appcontext
def seed_data():
    """填充示例测试数据（表已存在时使用）"""
    # 检查是否已有数据
    if TestSuite.query.count() > 0:
        click.echo('! 数据库已有数据，跳过初始化')
        return
    
    click.echo('开始初始化示例数据...')
    
    # 1. 创建测试套件
    suites_data = [
        {'name': '固件初始化测试', 'category': 'firmware', 'description': 'SSD固件初始化相关测试'},
        {'name': 'SATA协议测试', 'category': 'protocol', 'description': 'SATA接口协议兼容性测试'},
        {'name': 'NVMe功能测试', 'category': 'protocol', 'description': 'NVMe命令和功能测试'},
        {'name': 'PCIe链路测试', 'category': 'protocol', 'description': 'PCIe链路训练和稳定性测试'},
        {'name': '性能基准测试', 'category': 'performance', 'description': '读写性能基准测试'},
        {'name': '电源管理测试', 'category': 'power', 'description': '功耗和电源状态测试'},
    ]
    
    suites = []
    for data in suites_data:
        suite = TestSuite(**data)
        db.session.add(suite)
        suites.append(suite)
    
    db.session.flush()
    
    # 2. 创建测试用例
    cases_data = [
        # 固件初始化测试
        {
            'suite_id': suites[0].id,
            'name': 'FW_001_固件版本检查',
            'test_type': 'unit',
            'description': '验证固件版本号正确性',
            'script_type': 'pytest',
            'script_content': '''
def test_firmware_version():
    from ssd.firmware import Firmware
    fw = Firmware()
    version = fw.get_version()
    assert version.major == 2
    assert version.minor == 1
    assert version.patch == 3
''',
            'simulation_pass_rate': 0.95
        },
        {
            'suite_id': suites[0].id,
            'name': 'FW_002_初始化序列',
            'test_type': 'integration',
            'description': '验证固件初始化流程',
            'simulation_pass_rate': 0.9
        },
        {
            'suite_id': suites[0].id,
            'name': 'FW_003_配置加载',
            'test_type': 'unit',
            'description': '验证配置参数加载',
            'simulation_pass_rate': 0.85
        },
        # SATA协议测试
        {
            'suite_id': suites[1].id,
            'name': 'SATA_001_链路建立',
            'test_type': 'integration',
            'description': '验证SATA链路建立过程',
            'script_type': 'pytest',
            'script_content': '''
def test_sata_link_establishment():
    from ssd.protocol.sata import SATAController
    sata = SATAController()
    assert sata.link_up() == True
    assert sata.speed == '6Gbps'
''',
            'simulation_pass_rate': 0.8
        },
        {
            'suite_id': suites[1].id,
            'name': 'SATA_002_IDENTIFY命令',
            'test_type': 'unit',
            'description': '验证IDENTIFY DEVICE命令',
            'simulation_pass_rate': 0.95
        },
        {
            'suite_id': suites[1].id,
            'name': 'SATA_003_READ_DMA',
            'test_type': 'integration',
            'description': '验证DMA读操作',
            'simulation_pass_rate': 0.85
        },
        # NVMe功能测试
        {
            'suite_id': suites[2].id,
            'name': 'NVMe_001_控制器识别',
            'test_type': 'unit',
            'description': '验证Identify Controller',
            'script_type': 'pytest',
            'script_content': '''
def test_nvme_identify_controller():
    from ssd.protocol.nvme import NVMeController
    nvme = NVMeController()
    ctrl = nvme.id_ctrl()
    assert ctrl.vid == 0x1987
    assert ctrl.ssvid == 0x1987
''',
            'simulation_pass_rate': 0.9
        },
        {
            'suite_id': suites[2].id,
            'name': 'NVMe_002_命名空间列表',
            'test_type': 'unit',
            'description': '验证Namespace列表获取',
            'simulation_pass_rate': 0.9
        },
        {
            'suite_id': suites[2].id,
            'name': 'NVMe_003_READ命令',
            'test_type': 'integration',
            'description': '验证NVMe Read命令',
            'simulation_pass_rate': 0.85
        },
        # PCIe链路测试
        {
            'suite_id': suites[3].id,
            'name': 'PCIe_001_链路训练',
            'test_type': 'integration',
            'description': '验证PCIe链路训练',
            'simulation_pass_rate': 0.75
        },
        {
            'suite_id': suites[3].id,
            'name': 'PCIe_002_速度协商',
            'test_type': 'unit',
            'description': '验证链路速度协商',
            'simulation_pass_rate': 0.85
        },
        # 性能基准测试
        {
            'suite_id': suites[4].id,
            'name': 'PERF_001_顺序读',
            'test_type': 'performance',
            'description': '顺序读取性能测试',
            'script_type': 'pytest',
            'script_content': '''
import pytest
def test_sequential_read_iops():
    from ssd.performance import PerformanceTest
    perf = PerformanceTest()
    result = perf.sequential_read(block_size='128K', queue_depth=32)
    assert result.iops >= 350000
    assert result.bandwidth_mb >= 500
''',
            'simulation_pass_rate': 0.7
        },
        {
            'suite_id': suites[4].id,
            'name': 'PERF_002_顺序写',
            'test_type': 'performance',
            'description': '顺序写入性能测试',
            'simulation_pass_rate': 0.75
        },
        {
            'suite_id': suites[4].id,
            'name': 'PERF_003_随机读IOPS',
            'test_type': 'performance',
            'description': '随机读取IOPS测试',
            'simulation_pass_rate': 0.7
        },
        # 电源管理测试
        {
            'suite_id': suites[5].id,
            'name': 'PWR_001_空闲功耗',
            'test_type': 'unit',
            'description': '空闲状态功耗测试',
            'simulation_pass_rate': 0.9
        },
        {
            'suite_id': suites[5].id,
            'name': 'PWR_002_活跃功耗',
            'test_type': 'unit',
            'description': '读写状态功耗测试',
            'simulation_pass_rate': 0.85
        },
    ]
    
    for data in cases_data:
        case = TestCase(**data)
        db.session.add(case)
    
    db.session.flush()
    
    # 3. 创建示例测试计划
    all_case_ids = [case.id for case in TestCase.query.all()]
    
    plan = TestPlan(
        name='v2.1.3 回归测试（示例）',
        description='包含固件、协议、性能的全量回归测试',
        suite_ids=[s.id for s in suites],
        case_ids=all_case_ids,
        trigger_type='manual',
        parallel=True,
        max_concurrent=5,
        is_active=True
    )
    db.session.add(plan)
    
    # 4. 创建定时测试计划
    unit_cases = TestCase.query.filter_by(test_type='unit').limit(2).all()
    unit_case_ids = [c.id for c in unit_cases]
    unit_suite_ids = list(set([c.suite_id for c in unit_cases]))
    
    schedule_plan = TestPlan(
        name='定时单元测试（示例）',
        description='每5分钟自动执行的单元测试',
        suite_ids=unit_suite_ids,
        case_ids=unit_case_ids,
        trigger_type='schedule',
        schedule_cron='*/5 * * * *',
        parallel=False,
        max_concurrent=2,
        is_active=True
    )
    db.session.add(schedule_plan)
    db.session.commit()
    
    click.echo(f'✓ 示例数据初始化完成！')
    click.echo(f'  - 测试套件: {len(suites)} 个')
    click.echo(f'  - 测试用例: {len(cases_data)} 个')
    click.echo(f'  - 测试计划: 2 个（1个手动 + 1个定时）')
    click.echo(f'  - 登录账号: admin / admin123')


@click.command('clear-data')
@with_appcontext
def clear_data():
    """清空所有数据（保留表结构，不填充）"""
    click.confirm('确定要清空所有数据吗？此操作不可恢复！', abort=True)
    
    click.echo('清空数据...')
    
    # 按依赖顺序删除（先删子表，再删父表）
    count_plan = TestPlan.query.delete()
    count_case = TestCase.query.delete()
    count_suite = TestSuite.query.delete()
    
    db.session.commit()
    
    click.echo(f'✓ 数据已清空')
    click.echo(f'  - 删除测试计划: {count_plan} 个')
    click.echo(f'  - 删除测试用例: {count_case} 个')
    click.echo(f'  - 删除测试套件: {count_suite} 个')
    click.echo(f'  - 如需重新填充，请执行: flask seed-data')


# 命令列表
commands = [seed_data, clear_data]
