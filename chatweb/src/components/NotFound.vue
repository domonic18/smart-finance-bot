<template>
  <main class="container">
    <div class="text-center">
      <p class="status-code">404</p>
      <h1 class="title">Page not found</h1>
      <p class="message">Sorry, we couldn’t find the page you’re looking for.</p>
      <div class="button-container">
        <a href="#" class="home-button">Go back home</a>
      </div>
    </div>
  </main>
</template>

<style scoped>
.container {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background-color: white;
  padding: 6rem 1.5rem; /* px-6 py-24 */
}

.status-code {
  font-size: 1rem; /* text-base */
  font-weight: 600; /* font-semibold */
  color: #4f46e5; /* text-indigo-600 */
}

.title {
  margin-top: 1rem; /* mt-4 */
  font-size: 2rem; /* text-3xl */
  font-weight: 700; /* font-bold */
  letter-spacing: -0.025em; /* tracking-tight */
  color: #111827; /* text-gray-900 */
}

.message {
  margin-top: 1.5rem; /* mt-6 */
  font-size: 1rem; /* text-base */
  line-height: 1.5rem; /* leading-7 */
  color: #4b5563; /* text-gray-600 */
}

.button-container {
  margin-top: 2.5rem; /* mt-10 */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem; /* gap-x-6 */
}

.home-button {
  border-radius: 0.375rem; /* rounded-md */
  background-color: #4f46e5; /* bg-indigo-600 */
  padding: 0.625rem 0.875rem; /* px-3.5 py-2.5 */
  font-size: 0.875rem; /* text-sm */
  font-weight: 600; /* font-semibold */
  color: white; /* text-white */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); /* shadow-sm */
  transition: background-color 0.2s;
}

.home-button:hover {
  background-color: #4338ca; /* hover:bg-indigo-500 */
}

.home-button:focus-visible {
  outline: 2px solid #4f46e5; /* focus-visible:outline-indigo-600 */
  outline-offset: 2px; /* focus-visible:outline-offset-2 */
}
</style>
