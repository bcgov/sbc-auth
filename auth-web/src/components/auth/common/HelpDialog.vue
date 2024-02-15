<template>
  <component
    :is="componentType"
    v-if="isDialogOpen"
    v-model="isDialogOpen"
    max-width="45rem"
  >
    <v-card>
      <v-card-title>
        <h1>Need Help?</h1>
      </v-card-title>
      <v-card-text>
        <p
          class="mb-7"
          v-html="helpDialogBlurb"
        />

        <ul class="contact-info__list mb-7">
          <li>
            <span>{{ $t('labelTollFree') }}</span>
            &nbsp;
            <a :href="`tel:+${$t('maximusSupportTollFree')}`">{{ $t('maximusSupportTollFree') }}</a>
          </li>
          <li>
            <span>{{ $t('labelVictoriaOffice') }}</span>
            &nbsp;
            <a :href="`tel:+${$t('maximusSupportPhone')}`">{{ $t('maximusSupportPhone') }}</a>
          </li>
          <li>
            <span>{{ $t('labelEmail') }}</span>
            &nbsp;
            <a :href="'mailto:' + $t('maximusSupportEmail') + '?subject=' + $t('maximusSupportEmailSubject')">{{ $t('maximusSupportEmail') }}</a>
          </li>
        </ul>

        <p class="mb-0">
          <strong>{{ $t('labelHoursOfOperation') }}</strong><br>
          {{ $t('hoursOfOperation') }}
        </p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          large
          color="primary"
          @click="close()"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </component>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from '@vue/composition-api'

export default defineComponent({
  name: 'HelpDialog',
  props: {
    helpDialogBlurb: {
      type: String,
      default: ''
    },
    inline: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const isDialogOpen = ref(false)

    function open () {
      isDialogOpen.value = true
    }

    function close () {
      isDialogOpen.value = false
    }

    const componentType = computed<string>(() => {
      if (props.inline) {
        return 'div'
      } else {
        return 'v-dialog'
      }
    })

    return {
      isDialogOpen,
      open,
      close,
      componentType
    }
  }

})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/ModalDialog.scss';
</style>
