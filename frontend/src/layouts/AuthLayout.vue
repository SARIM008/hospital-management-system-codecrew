<script setup>
</script>

<template>
  <div class="auth-layout">
    <div class="auth-container card">
      <div class="auth-header text-center">
        <h2>Ward Wizard</h2>
        <p>Operational Management System</p>
      </div>
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background);
  padding: 1rem;
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-header {
  margin-bottom: 2rem;
}

.auth-header h2 {
  color: var(--primary);
  margin-bottom: 0.25rem;
}
</style>
