<template>
  <v-dialog
    :persistent="isPersistent"
    :fullscreen="fullscreenOnMobile"
    :scrollable="isScrollable"
    content-class="text-center"
    v-model="isOpen"
    @keydown.esc="cancel">
    <v-card>
      <v-card-title class="pt-8">
        <slot v-if="showIcon" name="icon">
          <v-icon large color="success">check</v-icon>
        </slot>
        <span class="mt-5">
          <slot name="title">{{ title }}</slot>
        </span>
      </v-card-title>
      <v-card-text>
        <slot name="text">{{ text }}</slot>
      </v-card-text>
      <v-card-actions v-if="showActions" class="pt-8 pb-8">
        <slot name="actions">
          <v-btn large color="success" @click="close()">OK</v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class ModalDialog extends Vue {
  private isOpen = false

  @Prop({ default: '' }) private title: string
  @Prop({ default: '' }) private text: string
  @Prop({ default: true }) private showIcon: boolean
  @Prop({ default: true }) private showActions: boolean
  @Prop({ default: false }) private isPersistent: boolean
  @Prop({ default: false }) private fullscreenOnMobile: boolean
  @Prop({ default: false }) private isScrollable: boolean

  public open () {
    this.isOpen = true
  }

  public close () {
    this.isOpen = false
  }
}
</script>

<style lang="scss">
.v-dialog {
    max-width: 35rem;

    .v-card__title {
      flex-direction: column;
    }

    .v-card__actions {
      justify-content: center;
    }
  }
</style>
