<template>
  <section>
    <h2 class="mb-5">
      {{ `${tabNumber !==null ? `${tabNumber}.` : ''} ${title}` }}
    </h2>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Notary Name
      </v-col>
      <v-col class="py-2">
        {{ accountNotaryName }}
      </v-col>
    </v-row>
    <v-row v-if="accountNotaryContact">
      <v-col class="cols-12 col-sm-3 py-2">
        Mailing Address
      </v-col>
      <v-col class="py-2">
        <div>
          <ul class="mailing-address">
            <li>{{ accountNotaryContact.street }}</li>
            <li>{{ accountNotaryContact.city }} {{ accountNotaryContact.region }} {{ accountNotaryContact.postalCode }}</li>
            <li>{{ accountNotaryContact.country }}</li>
          </ul>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Email Address
      </v-col>
      <v-col class="py-2">
        {{ accountNotaryContact.email }}
      </v-col>
    </v-row>
    <v-row>
      <v-col class="cols-12 col-sm-3 py-2">
        Phone Number
      </v-col>
      <v-col class="py-2">
        {{ accountNotaryContact.phone }}
      </v-col>
    </v-row>
  </section>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Contact } from '@/models/contact'

@Component({})
export default class NotaryInformation extends Vue {
  @Prop({ default: null }) private tabNumber: number
  @Prop({ default: 'Notary Information' }) private title: string
  @Prop({ default: {} }) accountNotaryContact: Contact
  @Prop({ default: '' }) accountNotaryName: string
}
</script>

<style lang="scss" scoped>

  .mailing-address {
    list-style-type: none;
    margin: 0;
    padding: 0;
  }
</style>
