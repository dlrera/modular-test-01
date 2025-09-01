<template>
  <v-app>
    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      color="secondary"
      permanent
      app
    >
      <v-list-item
        prepend-avatar="https://ui-avatars.com/api/?name=PM&background=216093&color=fff"
        title="Property Management"
        subtitle="Multi-Tenant Platform"
        class="pa-2"
        style="color: white !important;"
      />

      <v-divider />

      <v-list density="compact" nav style="color: white !important;">
        <v-list-item
          v-for="item in navigationItems"
          :key="item.title"
          :to="item.route"
          :prepend-icon="item.icon"
          :title="item.title"
          :disabled="item.disabled"
          style="color: white !important;"
          active-color="primary"
        >
          <v-tooltip
            v-if="item.disabled"
            activator="parent"
            location="end"
          >
            Coming Soon
          </v-tooltip>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <v-divider />
        <v-list density="compact" nav style="color: white !important;">
          <v-list-item
            prepend-icon="mdi-cog"
            title="Settings"
            to="/settings"
            style="color: white !important;"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            @click="handleLogout"
            style="color: white !important;"
          />
        </v-list>
      </template>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar color="white" elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer" class="d-md-none" />
      
      <v-toolbar-title>
        {{ currentPageTitle }}
      </v-toolbar-title>

      <v-spacer />

      <!-- User Menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-avatar size="32">
              <v-icon>mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
            <v-list-item-title>{{ userName }}</v-list-item-title>
            <v-list-item-subtitle>{{ userEmail }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item @click="handleProfile">
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item>
          <v-list-item @click="handleLogout">
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const drawer = ref(true)

// Navigation items configuration
const navigationItems = ref([
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    route: '/',
    disabled: false
  },
  {
    title: 'Documents',
    icon: 'mdi-file-document-multiple',
    route: '/documents',
    disabled: false
  },
  {
    title: 'PM Templates',
    icon: 'mdi-file-document-edit',
    route: '/pm-templates',
    disabled: true
  },
  {
    title: 'Risk Inspections',
    icon: 'mdi-clipboard-check',
    route: '/risk-inspections',
    disabled: true
  },
  {
    title: 'Properties',
    icon: 'mdi-office-building',
    route: '/properties',
    disabled: true
  },
  {
    title: 'Tenants',
    icon: 'mdi-account-group',
    route: '/tenants',
    disabled: true
  },
  {
    title: 'Maintenance',
    icon: 'mdi-wrench',
    route: '/maintenance',
    disabled: true
  },
  {
    title: 'Financial',
    icon: 'mdi-currency-usd',
    route: '/financial',
    disabled: true
  },
  {
    title: 'Reports',
    icon: 'mdi-chart-bar',
    route: '/reports',
    disabled: true
  }
])

// User information (would come from store/auth in real app)
const userName = ref('John Doe')
const userEmail = ref('john.doe@property.com')

// Computed
const currentPageTitle = computed(() => {
  const currentItem = navigationItems.value.find(item => item.route === route.path)
  return currentItem?.title || 'Property Management'
})

// Methods
function handleLogout() {
  // In real app, would handle logout
  console.log('Logout')
  router.push('/login')
}

function handleProfile() {
  router.push('/profile')
}
</script>

<style scoped>
/* Ensure white text in navigation drawer */
.v-navigation-drawer--active {
  color: white !important;
}

.v-list-item--active {
  background-color: rgba(33, 96, 147, 0.1);
}

.v-list-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
</style>