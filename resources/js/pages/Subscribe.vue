<script setup lang="ts">
import { Button } from '@/ui/button';
import { Input } from '@/ui/input';
import { Head } from '@inertiajs/vue3';
import { Heart, Mail } from 'lucide-vue-next';
import { onMounted, onUnmounted, ref } from 'vue';

const JSONP_URL = 'https://clayton.us2.list-manage.com/subscribe/post-json?u=d5c4aef36a582de40d5837112&id=8fc2472183&f_id=006179e0f0';
const PRIVACY_URL = 'https://clayton.tv/Clayton_TV_Data_Privacy_Notice.pdf';

const email = ref('');
const firstName = ref('');
const lastName = ref('');
const error = ref('');
const success = ref('');
const submitting = ref(false);
const formRef = ref<HTMLFormElement | null>(null);

function isValidEmail(value: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function submitToMailchimp(): Promise<{ result: string; msg: string }> {
    return new Promise((resolve, reject) => {
        const formData = new FormData(formRef.value!);
        const params = new URLSearchParams(formData as unknown as Record<string, string>);

        const callbackName = `mc_callback_${Date.now()}`;
        const url = `${JSONP_URL}&c=${callbackName}&${params.toString()}`;

        const script = document.createElement('script');
        script.setAttribute('type', 'text/javascript');
        script.async = true;
        script.src = url;

        const timeout = setTimeout(() => {
            cleanup();
            reject(new Error('Request timed out. Please try again.'));
        }, 10000);

        function cleanup() {
            clearTimeout(timeout);
            delete (window as unknown as Record<string, unknown>)[callbackName];
            if (script.parentNode) script.parentNode.removeChild(script);
        }

        (window as unknown as Record<string, unknown>)[callbackName] = (data: { result: string; msg: string }) => {
            cleanup();
            resolve(data);
        };

        script.onerror = () => {
            cleanup();
            reject(new Error('Network error. Please try again.'));
        };

        document.head.appendChild(script);
    });
}

async function handleSubmit() {
    if (!isValidEmail(email.value)) {
        error.value = 'Please enter a valid email address.';
        return;
    }
    error.value = '';
    success.value = '';
    submitting.value = true;

    try {
        const data = await submitToMailchimp();

        if (data.result === 'success') {
            success.value = data.msg;
        } else {
            // Mailchimp returns HTML and a leading error code (e.g. "0 - ...") — strip both
            error.value = data.msg
                .replace(/<[^>]*>/g, '')
                .replace(/^\d+\s*-\s*/, '')
                .trim();
        }
    } catch (e) {
        error.value = e instanceof Error ? e.message : 'Something went wrong. Please try again.';
    } finally {
        submitting.value = false;
    }
}

function clearErrorIfValid(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    if (error.value && isValidEmail(value)) {
        error.value = '';
    }
}

// CAF Donate widget
const CAF_SCRIPT_ID = 'CAFDonateWidgetLoader_script';
const CAF_CAMPAIGN_ID = 150;

onMounted(() => {
    if (document.getElementById(CAF_SCRIPT_ID)) return;

    (window as unknown as Record<string, unknown>)['caf_BeneficiaryCampaignId'] = CAF_CAMPAIGN_ID;
    (window as unknown as Record<string, unknown>)['fixSize'] = false;

    const script = document.createElement('script');
    script.id = CAF_SCRIPT_ID;
    script.type = 'text/javascript';
    script.src = 'https://cafdonate.cafonline.org/js/CAF.DonateWidgetLoader_script.js';
    document.head.appendChild(script);
});

onUnmounted(() => {
    const script = document.getElementById(CAF_SCRIPT_ID);
    if (script) script.remove();
    delete (window as unknown as Record<string, unknown>)['caf_BeneficiaryCampaignId'];
    delete (window as unknown as Record<string, unknown>)['fixSize'];
});
</script>

<template>
    <div>
        <Head title="Subscribe" />
        <div class="mx-auto max-w-2xl px-4 py-14 lg:px-8">
            <div class="flex items-start gap-3">
                <span class="bg-primary/10 text-primary flex h-10 w-10 flex-none items-center justify-center rounded-full" aria-hidden="true">
                    <Mail class="h-5 w-5" />
                </span>
                <div class="min-w-0">
                    <h1 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Subscribe</h1>
                </div>
            </div>

            <!-- Success state -->
            <div v-if="success" class="mt-8 rounded-lg border border-green-200 bg-green-50 p-6 text-center dark:border-green-800 dark:bg-green-950">
                <p class="text-lg font-medium text-green-800 dark:text-green-200">Check your inbox</p>
                <p class="text-muted-foreground mt-2 text-sm">{{ success }}</p>
            </div>

            <!-- Form state -->
            <template v-else>
                <p class="text-muted-foreground mt-6 leading-relaxed">
                    At Clayton.TV we strive to bring Christ-centred, biblical videos into one place with fresh content weekly. Our aim is to support
                    and equip Christians around the world. If you find our work helpful, and would like regular email updates from Clayton.TV, please
                    opt-in below (you can opt out at any time).
                </p>

                <form ref="formRef" novalidate class="mt-8 space-y-5" @submit.prevent="handleSubmit">
                    <p class="text-muted-foreground text-sm"><span class="text-destructive">*</span> indicates required</p>

                    <!-- Email (required) -->
                    <div>
                        <label for="mce-EMAIL" class="text-foreground mb-1.5 block text-sm font-medium">
                            Email Address <span class="text-destructive">*</span>
                        </label>
                        <Input
                            id="mce-EMAIL"
                            v-model="email"
                            type="email"
                            name="EMAIL"
                            required
                            autocomplete="email"
                            placeholder="you@example.com"
                            :class="{ 'border-destructive': error }"
                            @input="clearErrorIfValid"
                        />
                        <p v-if="error" class="text-destructive mt-1.5 text-sm" role="alert">
                            {{ error }}
                        </p>
                    </div>

                    <!-- Name fields -->
                    <div class="grid gap-4 sm:grid-cols-2">
                        <div>
                            <label for="mce-FNAME" class="text-foreground mb-1.5 block text-sm font-medium">First Name</label>
                            <Input id="mce-FNAME" v-model="firstName" type="text" name="FNAME" autocomplete="given-name" />
                        </div>
                        <div>
                            <label for="mce-LNAME" class="text-foreground mb-1.5 block text-sm font-medium">Last Name</label>
                            <Input id="mce-LNAME" v-model="lastName" type="text" name="LNAME" autocomplete="family-name" />
                        </div>
                    </div>

                    <!-- GDPR / Marketing permissions -->
                    <fieldset class="border-border space-y-3 border-t pt-5">
                        <legend class="text-foreground text-sm font-medium">Marketing Permissions</legend>
                        <p class="text-muted-foreground text-sm leading-relaxed">
                            Clayton TV will use the information you provide on this form to be in touch with you with regular email updates. Please
                            confirm you would like to hear from us:
                        </p>
                        <div class="flex items-center gap-2">
                            <input id="gdpr_669" type="checkbox" name="gdpr[669]" value="Y" class="accent-primary h-4 w-4" />
                            <label for="gdpr_669" class="text-foreground text-sm">Email</label>
                        </div>
                        <p class="text-muted-foreground text-xs leading-relaxed">
                            You can change your mind at any time by clicking the unsubscribe link in the footer of any email you receive from us, or
                            by contacting us at
                            <a href="mailto:enquiries@clayton.tv" class="text-primary underline-offset-4 hover:underline">enquiries@clayton.tv</a>. We
                            will treat your information with respect. For more information about our privacy practices please see our
                            <a :href="PRIVACY_URL" target="_blank" rel="noopener" class="text-primary underline-offset-4 hover:underline"
                                >privacy notice</a
                            >.
                        </p>
                    </fieldset>

                    <p class="text-muted-foreground text-xs leading-relaxed">
                        We use Mailchimp as our marketing platform. By clicking below to subscribe, you acknowledge that your information will be
                        transferred to Mailchimp for processing.
                        <a
                            href="https://mailchimp.com/legal/terms"
                            target="_blank"
                            rel="noopener"
                            class="text-primary underline-offset-4 hover:underline"
                            >Learn more</a
                        >
                        about Mailchimp's privacy practices.
                    </p>

                    <!-- Honeypot anti-bot field -->
                    <div aria-hidden="true" class="absolute -left-[5000px]">
                        <input type="text" name="b_d5c4aef36a582de40d5837112_8fc2472183" tabindex="-1" value="" />
                    </div>

                    <Button type="submit" size="lg" :disabled="submitting">
                        {{ submitting ? 'Subscribing…' : 'Subscribe' }}
                    </Button>
                </form>
            </template>
        </div>

        <!-- Donation section -->
        <div class="mx-auto max-w-2xl px-4 pb-14 lg:px-8">
            <hr class="border-border mb-10" />

            <div class="flex items-start gap-3">
                <span class="bg-primary/10 text-primary flex h-10 w-10 flex-none items-center justify-center rounded-full" aria-hidden="true">
                    <Heart class="h-5 w-5" />
                </span>
                <div class="min-w-0">
                    <h2 class="font-display text-foreground text-2xl font-bold sm:text-3xl">Donation</h2>
                </div>
            </div>

            <p class="text-muted-foreground mt-6 leading-relaxed">
                All our content is free so your donations are vital to the continuing work of Clayton TV. We'd love it if you'd like to partner with
                us financially - either as a one off or as a regular supporter
            </p>

            <div id="CAFDonateWidgetContainer" class="mt-8 h-[700px] w-full overflow-hidden rounded-lg"></div>

            <!-- Bank transfer -->
            <div class="border-border mt-10 rounded-lg border p-6">
                <h3 class="text-foreground text-base font-semibold">TO MAKE PAYMENTS VIA YOUR BANK</h3>
                <p class="text-muted-foreground mt-1 text-sm">Set up a one-off gift or a standing order directly with your bank.</p>

                <dl class="mt-4 space-y-2 text-sm">
                    <div class="grid grid-cols-2 gap-x-4">
                        <dt class="text-muted-foreground font-medium">Account name</dt>
                        <dd class="text-foreground">The Jesmond Trust</dd>
                    </div>
                    <div class="grid grid-cols-2 gap-x-4">
                        <dt class="text-muted-foreground font-medium">Sort code</dt>
                        <dd class="text-foreground">30-93-71</dd>
                    </div>
                    <div class="grid grid-cols-2 gap-x-4">
                        <dt class="text-muted-foreground font-medium">Account number</dt>
                        <dd class="text-foreground">00258445</dd>
                    </div>
                    <div class="grid grid-cols-2 gap-x-4">
                        <dt class="text-muted-foreground font-medium">Reference</dt>
                        <dd class="text-foreground">Clayton TV</dd>
                    </div>
                </dl>

                <p class="text-muted-foreground mt-4 text-sm">
                    Please email
                    <a href="mailto:enquiries@clayton.tv" class="text-primary underline-offset-4 hover:underline">enquiries@clayton.tv</a>
                    to let us know.
                </p>
            </div>

            <!-- Charity notice -->
            <p class="text-muted-foreground mt-6 text-xs leading-relaxed">
                Clayton TV is a ministry of the Jesmond Trust, registered charity 1193725. All donations are administered by the Jesmond Trust and
                online donations are processed through CAF.
            </p>
        </div>
    </div>
</template>
