<template>
  <v-card class="text-center">
    <v-card-title class="pt-8">
      <slot name="icon"></slot>
      <span class="mt-5">
        <slot name="title"></slot>
      </span>
    </v-card-title>
    <v-card-text>
      <slot name="text"></slot>
    </v-card-text>
    <v-card-actions class="pt-8 pb-8">
      <slot name="actions"></slot>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'AlertDialogContent',
  props: {
    iconColor: String
  }
}
</script>

<style lang="scss" scoped>
  @import "../assets/scss/theme.scss";

  .v-card__title {
    flex-direction: row;
    font-weight: 700;
  }

  .v-card__actions {
    justify-content: center;
  }

</style>
