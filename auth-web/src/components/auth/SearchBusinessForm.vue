<template>
    <v-container>
      <div class="view-container">
        <article>
          <h1>Search Co-operatives</h1>
          <!-- <p class="intro-text">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem. Aliquam erat volutpat. Donec placerat nisl magna, et faucibus arcu condimentum sed.</p>
          <v-divider></v-divider> -->
          <p class="intro-text"/>
          <p class="intro-text">Please enter the co-op's Incorporation number below to access their dashboard.</p>
              <h2>Incorporation Number</h2>
              <div class="search-for">
                <v-form ref="form" lazy-validation v-on:submit.prevent="searchBusiness">
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
                      filled
                      label="Incorporation Number"
                      hint="e.g. BC1234567"
                      req
                      persistent-hint
                      :rules="entityNumRules"
                      v-model="businessNumber"
                      id="txtBusinessNumber"
                    ></v-text-field>
                  </div>
                  <p class="intro-text"/>
                  <v-divider></v-divider>
                  <p class="intro-text"/>
                  <v-layout align-end justify-end>
                    <v-btn class="search-btn" @click="searchBusiness" color="primary" large >
                      <span>Enter</span>
                      <v-icon dark right>arrow_forward</v-icon>
                    </v-btn>
                  </v-layout>
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
export default class searchBusinessForm extends Vue {
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

  searchBusiness () {
    if (this.isFormValid()) {
        // attempt to searchBusiness
        this.businessStore.searchBusiness(this.businessNumber).then(()=>{
          this.errorMessage = ''
          // redirect to the coops UI
          window.location.href = this.VUE_APP_COPS_REDIRECT_URL
        }).catch (exception => {
          this.errorMessage = this.$t('noResultMsg').toString()
        })
    }
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

.v-btn.search-btn{
  font-weight : 700
}

.v-input {
  max-width : 25rem
}

</style>
