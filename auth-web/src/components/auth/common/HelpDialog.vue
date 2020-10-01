<template>
  <v-dialog v-model="isDialogOpen" max-width="640">
    <v-card>
      <v-card-title>Need Assistance?</v-card-title>
      <v-card-text>
        <p class="mb-7">If you have not received your Access Letter from BC Registries, or have lost your {{helpDialogFor}},
          <span>please contact us at:</span>
        </p>
        <ul class="contact-info__list mb-7">
          <li>
            <span>Toll Free:</span>&nbsp;&nbsp;{{ $t('techSupportTollFree') }}
          </li>
          <li>
            <span>Phone:</span>&nbsp;&nbsp;{{ $t('techSupportPhone') }}
          </li>
          <li>
            <span>Email:</span>&nbsp;&nbsp;<a v-bind:href="'mailto:' + $t('techSupportEmail') + '?subject=' + $t('techSupportEmailSubject')">{{ $t('techSupportEmail') }}</a>
          </li>
        </ul>
        <div>
          <p class="mb-0"><strong>Hours of Operation:</strong><br>Monday to Friday, 8:30am - 4:30pm <span title="Pacific Standard Time">PST</span></p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn large color="primary" @click="close()">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class HelpDialog extends Vue {
  private isDialogOpen = false

  @Prop({ default: '' }) private helpDialogFor: string

  public open () {
    this.isDialogOpen = true
  }

  public close () {
    this.isDialogOpen = false
  }
}
</script>
