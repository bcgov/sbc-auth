<template>
  <component :is="componentType" v-model="isDialogOpen" v-if="isDialogOpen" max-width="45rem">
    <v-card>
      <v-card-title>
        <h2>Need Help?</h2>
      </v-card-title>
      <v-card-text>
        <p class="mb-7" v-html="helpDialogBlurb" />

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
        <v-spacer></v-spacer>
        <v-btn large color="primary" @click="close()">Close</v-btn>
      </v-card-actions>
    </v-card>
  </component>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class HelpDialog extends Vue {
  isDialogOpen = false

  @Prop({ default: '' }) readonly helpDialogBlurb: string
  @Prop({ default: false }) readonly inline: boolean

  public open () {
    this.isDialogOpen = true
  }

  public close () {
    this.isDialogOpen = false
  }

  get componentType (): string {
    if (this.inline) {
      return 'div'
    } else {
      return 'v-dialog'
    }
  }
}
</script>


<style lang="scss" scoped>
  .v-card {
    > div {
        padding: 16px 40px 0 40px;
      &:first-of-type {
        padding: 40px 40px 0 40px;
      }
      &:last-of-type {
        padding: 40px 40px 40px 40px;
        button {
          padding: 0 20px;
        }
      }
    }
  }
</style>
