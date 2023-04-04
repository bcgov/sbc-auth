<template>
    <div class="observer" />
  </template>

<script>
export default {
  props: ['options'],
  data: () => ({
    observer: null
  }),
  mounted () {
    const options = this.options || {}
    this.observer = new IntersectionObserver(([entry]) => {
      if (entry && entry.isIntersecting) {
        this.$emit('intersect', entry)
      }
    }, options)
        this.observer?.observe(this.$el) // eslint-disable-line no-unused-expressions
  },
  beforeDestroy () {
        this.observer?.disconnect() // eslint-disable-line no-unused-expressions
  }
}
</script>

<style scoped>
.observer {
  min-height: 1px;
}
</style>
