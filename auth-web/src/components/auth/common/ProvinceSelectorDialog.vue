<template>
  <v-card>
    <v-card-title>Create a BC Registries Account</v-card-title>
    <v-card-text>
      <p class="mb-8">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem.  Aliquam erat volutpat. Donec placerat nisl magna, et faucibus arcu condimentum sed.</p>
      <v-radio-group v-model="selection">
        <v-radio value="yes">
          <template v-slot:label>
            <div>
              <div class="mb-2"><strong>I am a resident of British Columbia</strong></div>
              <div class="body-1">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem.  Aliquam erat volutpat. Donec placerat nisl magna, et faucibus arcu condimentum sed.</div>
            </div>
          </template>
        </v-radio>

        <div class="help-links body-2 mt-1 mb-10 ml-11">
          <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card/mobile-card" target="_blank">Learn more about the BC Services card</a>
          <span class="body-2 mx-4">OR</span>
          <router-link to="/extraprov-info/instructions">Verify with a notary instead</router-link>
        </div>

        <v-radio value="no">
          <template v-slot:label>
            <div>
              <div class="mb-2"><strong>I am not a resident of British Columbia</strong></div>
              <div class="body-1">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem.  Aliquam erat volutpat. Donec placerat nisl magna, et faucibus arcu condimentum sed.</div>
            </div>
          </template>
        </v-radio>
      </v-radio-group>
    </v-card-text>
    <v-card-actions class="form__btns pt-4 justify-end">
      <v-btn large color="primary" :disabled="!selection" @click="next()">Next<v-icon left class="ml-3">mdi-arrow-right</v-icon></v-btn>
      <v-btn large depressed @click="cancel()">Cancel</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
@Component({
  name: 'ProvinceSelectorDialog'
})
export default class ProvinceSelectorDialog extends Vue {
  @Prop({ default: false }) signedIn
  private selection = ''

  private next () {
    if (this.selection === 'yes') {
      if (this.signedIn) {
        this.$emit('bc-signed-in')
      } else {
        this.$emit('bc-not-signed-in')
      }
    } else {
      this.$emit('oop')
    }
  }

  private cancel () {
    this.$emit('close')
  }
}
</script>

<style scoped lang="scss">
  .v-radio {
    align-items: flex-start;
  }

 ::v-deep {
  .v-input--selection-controls__input {
    margin-top: -2px;
    margin-right: 20px !important;
  }

  .v-label strong {
    margin-top: 2px;
    color: #000000 !important;
  }

  .description {
    line-height: 1rem;
    font-size: 0.875rem;
  }
 }

 .help-links {
   margin: 0;
   padding: 0;
   list-style-type: none;

   .v-btn {
     text-decoration: underline;
   }
 }
</style>
