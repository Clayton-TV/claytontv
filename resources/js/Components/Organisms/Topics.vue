<script setup>
import { ref, computed } from "vue"
import LoadingSpinner from "../Atoms/LoadingSpinner.vue"

const categories = ref([
    "All",
    "Theology - Biblical Studies",
    "Theology - Sin",
    "Theology - God",
    "Theology - Salvation",
    "Theology - Jesus Christ",
    "Christian Life - Life Issues",
    "Christian Life - Spiritual Growth",
    "Family",
    "Church - Church Life",
    "Church - Practises",
    "Church - Leadership",
    "Worldview - Apologetics",
    "Worldview - Arts",
    "Worldview - Ethics",
    "Worldview - Public Life",
    "History",
])
const subCategories = ref([
    {
        category: "Theology - Biblical Studies",
        name: "Bible Book Overviews",
        videosCount: 95,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Bible Prophecy",
        videosCount: 28,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Bible Translation & Interpretation",
        videosCount: 14,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Inspiration & Inerrancy of the Bible",
        videosCount: 57,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Kingdom of God",
        videosCount: 52,
    },
    {
        category: "Theology - Biblical Studies",
        name: "New Testament Biblical Figures",
        videosCount: 78,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Old Testament Biblical Figures",
        videosCount: 36,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Redemptive History",
        videosCount: 5,
    },
    {
        category: "Theology - Biblical Studies",
        name: "The Covenants",
        videosCount: 1,
    },
    {
        category: "Theology - Biblical Studies",
        name: "Theology- Biblical/Systematic",
        videosCount: 10,
    },
    {
        category: "Theology - Sin",
        name: "Imputed & Original Sin",
        videosCount: 50,
    },
    {
        category: "Theology - Sin",
        name: "Indwelling Sin",
        videosCount: 58,
    },
    {
        category: "Theology - Sin",
        name: "Satan",
        videosCount: 44,
    },
    {
        category: "Theology - Sin",
        name: "The Fall",
        videosCount: 31,
    },
    {
        category: "Theology - Sin",
        name: "The Power & Effects of Sin",
        videosCount: 22,
    },
    {
        category: "Theology - God",
        name: "The Foreknowledge of God",
        videosCount: 71,
    },
    {
        category: "Theology - God",
        name: "The Glory of God",
        videosCount: 70,
    },
    {
        category: "Theology - God",
        name: "The Grace of God",
        videosCount: 20,
    },
    {
        category: "Theology - God",
        name: "The Holiness of God",
        videosCount: 62,
    },
    {
        category: "Theology - God",
        name: "The Holy Spirit",
        videosCount: 39,
    },
    {
        category: "Theology - God",
        name: "The Love of God",
        videosCount: 96,
    },
    {
        category: "Theology - God",
        name: "The Pleasures of God",
        videosCount: 45,
    },
    {
        category: "Theology - God",
        name: "The Sovereignty of God",
        videosCount: 58,
    },
    {
        category: "Theology - God",
        name: "The Trinity",
        videosCount: 92,
    },
    {
        category: "Theology - God",
        name: "The Wrath of God",
        videosCount: 95,
    },
    {
        category: "Theology - Salvation",
        name: "Creation",
        videosCount: 99,
    },
    {
        category: "Theology - Salvation",
        name: "End Times / Return of Christ",
        videosCount: 42,
    },
    {
        category: "Theology - Salvation",
        name: "Faith",
        videosCount: 33,
    },
    {
        category: "Theology - Salvation",
        name: "Glorification / Resurrection of the Body",
        videosCount: 76,
    },
    {
        category: "Theology - Salvation",
        name: "Heaven & Hell",
        videosCount: 3,
    },
    {
        category: "Theology - Salvation",
        name: "Justification",
        videosCount: 37,
    },
    {
        category: "Theology - Salvation",
        name: "Perseverance of the Saints",
        videosCount: 37,
    },
    {
        category: "Theology - Salvation",
        name: "Predestination/Election",
        videosCount: 20,
    },
    {
        category: "Theology - Salvation",
        name: "Regeneration / New Birth",
        videosCount: 13,
    },
    {
        category: "Theology - Salvation",
        name: "Repentance",
        videosCount: 41,
    },
    {
        category: "Theology - Salvation",
        name: "Sonship (Adoption by God)",
        videosCount: 43,
    },
    {
        category: "Theology - Salvation",
        name: "The Gospel",
        videosCount: 77,
    },
    {
        category: "Theology - Salvation",
        name: "The Law",
        videosCount: 40,
    },
    {
        category: "Theology - Jesus Christ",
        name: "The Birth of Christ/Incarnation",
        videosCount: 1,
    },
    {
        category: "Theology - Jesus Christ",
        name: "The Death of Christ/Atonement/Priesthood",
        videosCount: 75,
    },
    {
        category: "Theology - Jesus Christ",
        name: "The Deity of Christ/Person of Christ",
        videosCount: 55,
    },
    {
        category: "Theology - Jesus Christ",
        name: "The Life of Christ/Work/Miracles",
        videosCount: 49,
    },
    {
        category: "Theology - Jesus Christ",
        name: "The Resurrection of Christ",
        videosCount: 39,
    },
    {
        category: "Theology - Jesus Christ",
        name: "The Supremacy of Christ",
        videosCount: 80,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Assurance of Salvation/Doubt",
        videosCount: 39,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Biblical Counseling",
        videosCount: 57,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Conscience",
        videosCount: 97,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Courage & Boldness",
        videosCount: 45,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Death & Dying",
        videosCount: 11,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Encouragement",
        videosCount: 19,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Fear & Anxiety",
        videosCount: 93,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Fellowship & Hospitality",
        videosCount: 23,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Forgiving Others",
        videosCount: 1,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Gratitude/Contentment",
        videosCount: 31,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Hope/Joy",
        videosCount: 73,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Knowing God's Will/Guidance",
        videosCount: 14,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Life of the Body",
        videosCount: 77,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Loving Others",
        videosCount: 74,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Money",
        videosCount: 86,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Persecution & Martyrdom",
        videosCount: 44,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Pride & Humility",
        videosCount: 89,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Sexual Purity/Relationships",
        videosCount: 55,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Speech",
        videosCount: 2,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Spiritual Warfare/Temptation",
        videosCount: 45,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Suffering/Sickness",
        videosCount: 11,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Suicide",
        videosCount: 16,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Wisdom",
        videosCount: 88,
    },
    {
        category: "Christian Life - Life Issues",
        name: "Work & Vocation",
        videosCount: 14,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Christian Freedom",
        videosCount: 64,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Devotional Life/Quiet Times",
        videosCount: 71,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Discipleship",
        videosCount: 91,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Education",
        videosCount: 81,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Fasting",
        videosCount: 57,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Fruit of the Spirit",
        videosCount: 5,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Giving",
        videosCount: 35,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Life of the Mind",
        videosCount: 81,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Personal Holiness/Obedience",
        videosCount: 16,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Prayer",
        videosCount: 38,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Sanctification and Growth, God's Discipline",
        videosCount: 77,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Spiritual Gifts/Serving",
        videosCount: 47,
    },
    {
        category: "Christian Life - Spiritual Growth",
        name: "Testimony",
        videosCount: 31,
    },
    {
        category: "Family",
        name: "Biblical Manhood & Womanhood",
        videosCount: 37,
    },
    {
        category: "Family",
        name: "Children",
        videosCount: 8,
    },
    {
        category: "Family",
        name: "Divorce & Remarriage",
        videosCount: 23,
    },
    {
        category: "Family",
        name: "Marriage",
        videosCount: 58,
    },
    {
        category: "Family",
        name: "Men",
        videosCount: 13,
    },
    {
        category: "Family",
        name: "Parenting",
        videosCount: 94,
    },
    {
        category: "Family",
        name: "Women",
        videosCount: 8,
    },
    {
        category: "Church - Church Life",
        name: "Christian Unity",
        videosCount: 24,
    },
    {
        category: "Church - Church Life",
        name: "Multi-Site Church Ministry",
        videosCount: 63,
    },
    {
        category: "Church - Church Life",
        name: "Nature of the Church/Church Issues",
        videosCount: 6,
    },
    {
        category: "Church - Church Life",
        name: "Small Groups",
        videosCount: 7,
    },
    {
        category: "Church - Practises",
        name: "Baptism & Church Membership",
        videosCount: 99,
    },
    {
        category: "Church - Practises",
        name: "Christmas",
        videosCount: 68,
    },
    {
        category: "Church - Practises",
        name: "Church Discipline",
        videosCount: 60,
    },
    {
        category: "Church - Practises",
        name: "Easter",
        videosCount: 8,
    },
    {
        category: "Church - Practises",
        name: "The Lord's Day",
        videosCount: 24,
    },
    {
        category: "Church - Practises",
        name: "The Lord's Supper",
        videosCount: 59,
    },
    {
        category: "Church - Practises",
        name: "Church Planting",
        videosCount: 65,
    },
    {
        category: "Church - Practises",
        name: "Evangelism",
        videosCount: 54,
    },
    {
        category: "Church - Practises",
        name: "Ministry/Urban Ministry",
        videosCount: 35,
    },
    {
        category: "Church - Practises",
        name: "Missions",
        videosCount: 61,
    },
    {
        category: "Church - Practises",
        name: "Worship",
        videosCount: 7,
    },
    {
        category: "Church - Leadership",
        name: "Biblical Eldership",
        videosCount: 7,
    },
    {
        category: "Church - Leadership",
        name: "Pastoral Ministry",
        videosCount: 17,
    },
    {
        category: "Church - Leadership",
        name: "Preaching & Teaching",
        videosCount: 78,
    },
    {
        category: "Church - Leadership",
        name: "Spiritual Leadership",
        videosCount: 26,
    },
    {
        category: "Church - Leadership",
        name: "Women's Ministry",
        videosCount: 73,
    },
    {
        category: "Church - Leadership",
        name: "Youth and Children's Ministry",
        videosCount: 76,
    },
    {
        category: "Worldview - Apologetics",
        name: "Atheism",
        videosCount: 56,
    },
    {
        category: "Worldview - Apologetics",
        name: "Cults & The Occult",
        videosCount: 19,
    },
    {
        category: "Worldview - Apologetics",
        name: "Evidence for the Faith",
        videosCount: 90,
    },
    {
        category: "Worldview - Apologetics",
        name: "False Teaching",
        videosCount: 87,
    },
    {
        category: "Worldview - Apologetics",
        name: "General Apologetics",
        videosCount: 9,
    },
    {
        category: "Worldview - Apologetics",
        name: "Tough Texts",
        videosCount: 4,
    },
    {
        category: "Worldview - Apologetics",
        name: "Truth",
        videosCount: 86,
    },
    {
        category: "Worldview - Apologetics",
        name: "World Religions",
        videosCount: 67,
    },
    {
        category: "Worldview - Arts",
        name: "Art/Literature",
        videosCount: 18,
    },
    {
        category: "Worldview - Ethics",
        name: "Abortion/Bioethics",
        videosCount: 93,
    },
    {
        category: "Worldview - Ethics",
        name: "Gender",
        videosCount: 10,
    },
    {
        category: "Worldview - Ethics",
        name: "Homosexuality",
        videosCount: 17,
    },
    {
        category: "Worldview - Ethics",
        name: "Poverty",
        videosCount: 59,
    },
    {
        category: "Worldview - Ethics",
        name: "Public Justice",
        videosCount: 30,
    },
    {
        category: "Worldview - Ethics",
        name: "Racial Harmony",
        videosCount: 81,
    },
    {
        category: "Worldview - Ethics",
        name: "Social Issues",
        videosCount: 87,
    },
    {
        category: "Worldview - Public Life",
        name: "Christianity in Public Life",
        videosCount: 6,
    },
    {
        category: "Worldview - Public Life",
        name: "Culture",
        videosCount: 97,
    },
    {
        category: "Worldview - Public Life",
        name: "Education",
        videosCount: 49,
    },
    {
        category: "Worldview - Public Life",
        name: "Environment",
        videosCount: 21,
    },
    {
        category: "Worldview - Public Life",
        name: "Government/Politics",
        videosCount: 99,
    },
    {
        category: "Worldview - Public Life",
        name: "Middle East",
        videosCount: 95,
    },
    {
        category: "Worldview - Public Life",
        name: "Terrorism",
        videosCount: 50,
    },
    {
        category: "History",
        name: "Christian Biography",
        videosCount: 28,
    },
    {
        category: "History",
        name: "Church History",
        videosCount: 54,
    },
])
const sortedCategories = computed(() => {
    return categories.value.sort((a, b) => a.localeCompare(b))
})
const filteredSubCategories = computed(() => {
    const sortedSubCategories = subCategories.value.sort((a, b) =>
        a.name.localeCompare(b.name)
    )
    if (selectedCategory.value === "All") {
        return sortedSubCategories
    }
    return sortedSubCategories.filter(
        ({ category }) => category === selectedCategory.value
    )
})

let selectedCategory = ref("All")
let isLoadingSubCategories = ref(false)

function selectCategory(category) {
    isLoadingSubCategories.value = true
    setTimeout(() => {
        selectedCategory.value = category
        isLoadingSubCategories.value = false
    }, 500)
}
</script>

<template>
    <div class="mb-4 justify-items-center space-y-2">
        <h2 class="text-center text-3xl font-bold text-gray-100">
            Explore Topics
        </h2>
        <p class="text-center text-gray-400">
            There are a variety of topics for you to discover
        </p>
    </div>
    <div class="w-full items-center justify-center overflow-x-hidden pt-4">
        <ul class="flex snap-x snap-mandatory gap-x-0 overflow-x-auto px-2">
            <li
                v-for="(category, index) in sortedCategories"
                :key="index"
                class="relative isolate mb-3 flex w-auto shrink-0 snap-center flex-col justify-end gap-y-2 rounded-md">
                <button
                    class="me-2 rounded-full px-4 py-2 font-bold text-white hover:bg-red-400"
                    :class="
                        category === selectedCategory
                            ? 'bg-claytonRed'
                            : 'bg-gray-700'
                    "
                    @click="selectCategory(category)">
                    {{ category }}
                </button>
            </li>
        </ul>
    </div>
    <div class="w-full px-4 pb-4">
        <LoadingSpinner
            v-if="isLoadingSubCategories"
            class="h-[100vh] w-[100vw]"></LoadingSpinner>
        <div v-else>
            <h1 class="my-4 text-lg">
                Subcategories for:
                <span class="text-xl font-bold">{{ selectedCategory }}</span>
            </h1>
            <ul
                class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-2 sm:gap-x-6 lg:grid-cols-3 xl:gap-x-8">
                <li
                    v-for="(subcategory, index) in filteredSubCategories"
                    :key="index"
                    class="relative">
                    <div class="aspect-[5/1] rounded-lg bg-blue-950 p-4">
                        <div class="my-auto">
                            <h2 class="font-bold">{{ subcategory.name }}</h2>
                            <div class="block">
                                {{ subcategory.videosCount }} programme{{
                                    subcategory.videosCount > 1 ? "s" : ""
                                }}
                            </div>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</template>
