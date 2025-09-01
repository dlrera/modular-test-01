<template>
  <v-app>
    <v-main class="login-background">
      <v-container fluid fill-height>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="4">
            <v-card elevation="8" rounded="lg">
              <v-card-title class="text-h5 bg-primary text-white pa-6">
                Property Management System
              </v-card-title>
              
              <v-card-text class="pa-6">
                <v-form @submit.prevent="handleLogin" ref="loginForm">
                  <v-text-field
                    v-model="email"
                    label="Email"
                    type="email"
                    variant="outlined"
                    prepend-inner-icon="mdi-email"
                    :rules="[rules.required, rules.email]"
                    class="mb-4"
                  />
                  
                  <v-text-field
                    v-model="password"
                    label="Password"
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    prepend-inner-icon="mdi-lock"
                    :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showPassword = !showPassword"
                    :rules="[rules.required]"
                    class="mb-4"
                  />
                  
                  <v-checkbox
                    v-model="rememberMe"
                    label="Remember me"
                    color="primary"
                    class="mb-4"
                  />
                  
                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    :loading="loading"
                  >
                    Sign In
                  </v-btn>
                </v-form>
                
                <v-divider class="my-4" />
                
                <div class="text-center">
                  <a href="#" class="text-primary text-decoration-none">
                    Forgot password?
                  </a>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loginForm = ref()
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const loading = ref(false)

const rules = {
  required: (v: any) => !!v || 'Required',
  email: (v: string) => /.+@.+\..+/.test(v) || 'Invalid email'
}

async function handleLogin() {
  const valid = await loginForm.value.validate()
  if (!valid.valid) return
  
  loading.value = true
  
  // Simulate login - in real app would call auth API
  setTimeout(() => {
    loading.value = false
    router.push('/')
  }, 1000)
}
</script>

<style scoped>
.login-background {
  background: linear-gradient(135deg, #216093 0%, #001B48 100%);
}
</style>