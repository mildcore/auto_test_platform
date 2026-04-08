import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

import Login from '@/views/Login.vue'
import Layout from '@/views/Layout.vue'
import Dashboard from '@/views/Dashboard.vue'
import PlanList from '@/views/plans/List.vue'
import PlanForm from '@/views/plans/Form.vue'
import TaskList from '@/views/tasks/List.vue'
import TaskDetail from '@/views/tasks/Detail.vue'
import SuiteList from '@/views/suites/List.vue'
import About from '@/views/About.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '仪表盘' }
      },
      {
        path: 'plans',
        name: 'PlanList',
        component: PlanList,
        meta: { title: '测试计划' }
      },
      {
        path: 'plans/create',
        name: 'PlanCreate',
        component: PlanForm,
        meta: { title: '创建计划' }
      },
      {
        path: 'plans/:id/edit',
        name: 'PlanEdit',
        component: PlanForm,
        meta: { title: '编辑计划' }
      },
      {
        path: 'tasks',
        name: 'TaskList',
        component: TaskList,
        meta: { title: '测试任务' }
      },
      {
        path: 'tasks/:id',
        name: 'TaskDetail',
        component: TaskDetail,
        meta: { title: '任务详情' }
      },
      {
        path: 'suites',
        name: 'SuiteList',
        component: SuiteList,
        meta: { title: '测试套件' }
      },
      {
        path: 'about',
        name: 'About',
        component: About,
        meta: { title: '关于' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (!to.meta.public && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router
