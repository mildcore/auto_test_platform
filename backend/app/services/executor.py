"""
测试执行引擎
"""
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestExecutor:
    """测试执行器 - 模拟固件测试执行"""
    
    def __init__(self):
        self.max_workers = 5
    
    def run(self, task, app_context=None):
        """
        执行测试任务
        
        Args:
            task: TestTask对象
            app_context: Flask应用上下文（Celery中使用）
        
        Returns:
            dict: 执行结果和报告
        """
        # 如果需要app_context（Celery中），则使用它
        if app_context:
            with app_context():
                return self._execute(task, app_context)
        return self._execute(task, app_context)
    
    def _execute(self, task, app_context=None):
        """实际执行逻辑"""
        from app.repositories.case_repo import CaseRepository
        from app.extensions import db
        
        case_repo = CaseRepository()
        
        # 获取要执行的用例
        suite_ids = task.suite_ids or []
        cases = case_repo.get_by_suite_ids(suite_ids)
        
        # 如果指定了case_ids，按case_ids的顺序过滤并排序用例
        case_ids = task.case_ids or []
        if case_ids:
            case_map = {c.id: c for c in cases}
            ordered_cases = []
            for case_id in case_ids:
                if case_id in case_map:
                    ordered_cases.append(case_map[case_id])
            cases = ordered_cases
        
        if not cases:
            return {
                'status': 'failed',
                'total': 0,
                'passed': 0,
                'failed': 0,
                'error': 0,
                'report': {
                    'summary': {
                        'status': 'failed',
                        'error_message': '没有找到要执行的测试用例'
                    },
                    'executions': []
                }
            }
        
        # 执行统计
        total = len(cases)
        passed = 0
        failed = 0
        error = 0
        executions = []
        
        # 串行或并行执行
        if task.parallel:
            results = self._execute_parallel(cases, task.max_concurrent, app_context)
        else:
            results = self._execute_sequential(cases, app_context)
        
        for result in results:
            executions.append(result)
            if result['status'] == 'passed':
                passed += 1
            elif result['status'] == 'failed':
                failed += 1
            else:
                error += 1
        
        # 确定最终状态
        if passed == total:
            status = 'passed'
        else:
            status = 'failed'
        
        # 生成报告
        report = {
            'summary': {
                'task_id': task.id,
                'task_name': task.name,
                'status': status,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': datetime.utcnow().isoformat(),
                'total_cases': total,
                'passed_cases': passed,
                'failed_cases': failed,
                'error_cases': error,
                'pass_rate': round((passed / total) * 100, 2) if total > 0 else 0
            },
            'executions': executions
        }
        
        return {
            'status': status,
            'total': total,
            'passed': passed,
            'failed': failed,
            'error': error,
            'report': report
        }
    
    def _execute_sequential(self, cases, app_context=None):
        """串行执行"""
        results = []
        for case in cases:
            result = self._run_single_case(case, app_context)
            results.append(result)
        return results
    
    def _execute_parallel(self, cases, max_concurrent, app_context=None):
        """并行执行 - 每个线程都需要应用上下文"""
        results = []
        with ThreadPoolExecutor(max_workers=min(max_concurrent, self.max_workers)) as executor:
            # 提交任务时传递 app_context
            futures = {
                executor.submit(self._run_single_case, case, app_context): case 
                for case in cases
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        return results
    
    def _run_single_case(self, case, app_context=None):
        """执行单个测试用例（模拟）"""
        start_time = time.time()
        
        # 如果有 app_context，在线程中使用它
        if app_context:
            from flask import current_app
            if not current_app:
                # 在新线程中需要重新进入上下文
                with app_context():
                    return self._do_run_case(case, start_time)
        
        return self._do_run_case(case, start_time)
    
    def _do_run_case(self, case, start_time):
        """实际执行用例逻辑"""
        # 模拟执行延迟（0.5-3秒）
        time.sleep(random.uniform(0.5, 3.0))
        
        # 根据配置的通过率决定结果
        pass_rate = case.simulation_pass_rate or 0.9
        is_passed = random.random() < pass_rate
        
        execution_time = time.time() - start_time
        
        # 获取套件名称（在上下文内访问）
        suite_name = None
        try:
            suite_name = case.suite.name if case.suite else None
        except:
            suite_name = f'套件{case.suite_id}'
        
        if is_passed:
            status = 'passed'
            output = f"""[模拟执行]
测试用例: {case.name}
[初始化] 测试环境准备完成
[执行] 开始执行测试...
[通过] 执行成功
[耗时] {execution_time:.2f} 秒"""
            
            error_msg = None
        else:
            status = 'failed'
            output = f"""[模拟执行]
测试用例: {case.name}
[初始化] 测试环境准备完成
[执行] 开始执行测试...
[失败] 执行失败
[错误] 检测到异常: 响应超时/校验失败
[耗时] {execution_time:.2f} 秒"""
            
            error_msg = random.choice(['响应超时', '校验失败', '设备未就绪', '协议错误'])
        
        return {
            'case_id': case.id,
            'case_name': case.name,
            'suite_id': case.suite_id,
            'suite_name': suite_name,
            'test_type': case.test_type,
            'status': status,
            'execution_time': round(execution_time, 2),
            'output': output,
            'error': error_msg,
            'script_note': f'[预留] script_type: {case.script_type}, 可接入真实测试框架' if case.script_content else '[预留] 无脚本，纯模拟执行'
        }
