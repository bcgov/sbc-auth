<template>
    <v-container>
      <div class="view-container">
        <article>
          <h1>Search Co-operatives</h1>
          <p class="intro-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem. Aliquam erat volutpat. Donec placerat nisl magna, et faucibus arcu condimentum sed.</p>
          <v-divider></v-divider>
          <p class="intro-text"/>
          <p class="intro-text">Please enter the co-op's Incorporation number below to access their dashboard.</p>
              <h2>Incorporation Number</h2>
              <div class="search-for">
                <v-form ref="form" lazy-validation>
                  <div class="loading-msg" v-if="errorMessage">
                    <v-alert
                     :value="true"
                     color="error"
                     icon="warning"
                    >{{errorMessage}}
                    </v-alert>
                  </div>

                  <div class="search-for__row">
                    <v-text-field
                      box
                      label="Incorporation Number"
                      hint="e.g. BC1234567"
                      req
                      persistent-hint
                      :rules="entityNumRules"
                      v-model="businessNumber"
                    ></v-text-field>
                  </div>
                  <p class="intro-text"/>
                  <v-divider></v-divider>
                  <p class="intro-text"/>
                  <div>
                    <v-flex class="text-xs-right">
                      <v-btn class="search-btn" @click="staffSearch" color="primary" large>
                        <span>Enter</span>
                        <v-icon dark right>arrow_forward</v-icon>
                      </v-btn>
                    </v-flex>
                  </div>
                </v-form>
              </div>
        </article>
        <aside>
          <SupportInfoCard/>
        </aside>
      </div>
    </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Prop, Emit } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '../../store/modules/business'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import configHelper from '../../util/config-helper'

@Component({
  components: {
    SupportInfoCard
  }
})
export default class staffSearchForm extends Vue {
  VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  $refs: {
    form: HTMLFormElement
  }

  entityNumRules = [
    v => !!v || 'Incorporation Number is required'
  ]

  businessStore = getModule(BusinessModule, this.$store)

  businessNumber: string = ''
  errorMessage:string = ''

  private isFormValid (): boolean {
    return this.$refs.form.validate()
  }

  async staffSearch () {
    if (this.isFormValid()) {
      try {
        // attempt to staffSearch
        await this.businessStore.staffSearch(this.businessNumber)
        this.errorMessage = ''
        // redirect to the coops UI
        window.location.href = this.VUE_APP_COPS_REDIRECT_URL
      } catch (exception) {
        this.errorMessage = this.$t('noResultMsg').toString()
      }
    }
  }
}
</script>

<style lang="stylus" scoped>
@import '../../assets/styl/theme.styl';

.v-btn.search-btn
  font-weight 700

.v-input
  max-width 25rem

@media (max-width 600px)
  .v-btn.search-btn
    width 100%
</style>
