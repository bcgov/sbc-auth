<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" lg="8" class="text-center">
        <v-icon size="48" color="error" class="mb-6">mdi-alert-circle-outline</v-icon>
        <h1 class="mb-7">{{ $t('pageNotFoundTitle')}}</h1>
        <p class="mb-9">{{ $t('pageNotFoundMsg')}}</p>
        <v-btn large link color="primary" href="../">{{ $t('homeBtnLabel')}}</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

export default ({
  name: 'PageNotFound',
  components: {
  }
})
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .container {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }

  .v-icon {
    font-size: 4rem;
  }
</style>
