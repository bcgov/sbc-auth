<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="45rem"
  >
    <v-card>
      <v-card-title>Need Assistance?</v-card-title>
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
          OK
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class HelpDialog extends Vue {
  private isDialogOpen = false

  @Prop({ default: '' }) readonly helpDialogBlurb: string

  public open () {
    this.isDialogOpen = true
  }

  public close () {
    this.isDialogOpen = false
  }
}
</script>
