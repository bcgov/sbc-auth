<template>
  <div id="help-toggle-container">
    <v-btn
      text
      color="primary"
      class="help-btn px-0"
      :ripple="false"
      @click="isHelpContentOpen = !isHelpContentOpen"
    >
      <v-icon class="mr-1">
        mdi-help-circle-outline
      </v-icon>
      {{ isHelpContentOpen ? 'Hide ' + title : title }}
    </v-btn>
    <v-expand-transition>
      <div v-show="isHelpContentOpen" class="help-content mb-10">
        <hr class="my-4" />
        <slot class="content"></slot>
        <div class="align-right" v-if="showBottomToggle">
          <v-btn
            text
            color="primary"
            class="hide-help-btn pa-0"
            :ripple="false"
            @click="isHelpContentOpen = !isHelpContentOpen"
          >
            Hide Help
          </v-btn>
        </div>
        <hr class="my-4" />
      </div>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from '@vue/composition-api'

export default defineComponent({
  name: 'SimleHelpToggle',
  props: {
    toggleButtonTitle: { default: '' },
    /* show or hide secondary toggle within content */
    hasBottomHideToggle: { default: true }
  },
  setup (props) {
    const localState = reactive({
  isHelpContentOpen: false,
  title: props.toggleButtonTitle,
  showBottomToggle: props.hasBottomHideToggle
}) as { isHelpContentOpen: boolean, title: string, showBottomToggle: boolean };


    return {
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#help-toggle-container::v-deep {
  // Remove background on hover
  .help-btn::before,
  .hide-help-btn::before {
    display: none;
  }

  .help-btn {
    font-size: 16px;
    height: 24px;
  }

  .hide-help-btn {
    font-size: 14px;
    text-decoration: underline;
    height: 25px;
  }

  .help-content {
    h3 {
      color: $gray9;
    }
    h4,
    p {
      color: $gray7;
    }
    hr {
      border-top: 1px dashed $gray6;
    }
  }
}
</style>
