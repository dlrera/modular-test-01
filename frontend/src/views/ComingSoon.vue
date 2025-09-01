<template>
  <v-container>
    <v-row justify="center" align="center" style="min-height: 60vh;">
      <v-col cols="12" md="6" class="text-center">
        <v-icon size="100" color="primary" class="mb-4">
          mdi-rocket-launch
        </v-icon>
        <h1 class="text-h4 font-weight-medium mb-4">
          Coming Soon
        </h1>
        <p class="text-body-1 text-medium-emphasis">
          This feature is currently under development and will be available soon.
        </p>
        <v-btn
          color="primary"
          variant="outlined"
          to="/"
          class="mt-6"
        >
          <v-icon start>mdi-arrow-left</v-icon>
          Back to Dashboard
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
</script>