import AdminProfile from '@/components/AdminProfile.vue'
import CandidateProfile from '@/components/CandidateProfile.vue'
import Dashboard from '@/components/Dashboard.vue'
import ElectionList from '@/components/ElectionList.vue'
import RegisterCandidate from '@/components/RegisterCandidate.vue'
import RegisterVoter from '@/components/RegisterVoter.vue'
import DefaultView from '@/views/DefaultView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import { createRouter, createWebHistory } from 'vue-router'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: DefaultView,
      children: [
        {
          path: '',
          name: '',
          redirect: 'login'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: Dashboard,
        },
        {
          path: 'admin',
          name: 'admin',
          component: AdminProfile,
        },
        {
          path: 'elections',
          name: 'elections',
          component: ElectionList,
        },
        {
          path: 'candidate',
          name: 'candidate',
          component: CandidateProfile,
        },
        {
          path: 'register/voter',
          name: 'register/voter',
          component: RegisterVoter,
        },
        {
          path: 'register/candidate',
          name: 'register/candidate',
          component: RegisterCandidate,
        },
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    // {
    //   path: '/:pathMatch(.*)*',
    //   name: 'NotFound',
    //   component: NotFound
    // },


    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue'),
    // },
  ],
})


// router.beforeEach((to, from, next) => {
//   const authStore = useAuthStore();
//   if (to.meta.requiresAuth && !authStore.isAuthenticated) {
//     next('/login');
//   } else if (to.meta.role && authStore.userRole !== to.meta.role) {
//     next('/login');
//   } else {
//     next();
//   }
// });


export default router
