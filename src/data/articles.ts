import type { Article } from "@/types";
import { authors } from "./authors";
import { categories } from "./categories";
import { tags as T } from "./tags";

const a = (slug: string) => authors.find((x) => x.slug === slug)!;
const c = (slug: string) => categories.find((x) => x.slug === slug)!;

/** Cover dari picsum (deterministik per seed). 16:9. */
const cover = (seed: string) => `https://picsum.photos/seed/${seed}/1280/720`;

/** Body HTML contoh dengan heading ber-id (untuk TOC) + elemen kaya. */
function buildBody(lead: string, topic: string): string {
  return `
<p class="lead">${lead}</p>

<h2 id="latar">Latar di balik isu</h2>
<p>Selama beberapa bulan terakhir, ${topic} bergerak lebih cepat dari yang
diperkirakan banyak pengamat. Perubahan ini tidak terjadi dalam ruang hampa —
ada rangkaian keputusan, kepentingan, dan kebetulan yang membentuknya.</p>
<p>Kami menelusuri dokumen publik, berbicara dengan sejumlah narasumber, dan
membandingkan klaim dengan data yang tersedia. Hasilnya menunjukkan gambaran
yang lebih bernuansa ketimbang yang ramai dibagikan di lini masa.</p>

<figure>
  <img src="${cover("body-" + topic.length)}" alt="Ilustrasi pendukung artikel"
       width="1280" height="720" loading="lazy" decoding="async" />
  <figcaption>Ilustrasi. Foto bersifat dummy untuk pratinjau tata letak.</figcaption>
</figure>

<h2 id="temuan">Temuan utama</h2>
<p>Ada tiga hal yang menonjol dari penelusuran kami:</p>
<ul>
  <li><strong>Pertama</strong>, tren ini didorong oleh faktor struktural, bukan sekadar musiman.</li>
  <li><strong>Kedua</strong>, dampaknya tidak merata — sebagian kelompok diuntungkan, sebagian tertinggal.</li>
  <li><strong>Ketiga</strong>, ruang kebijakan masih terbuka, asalkan keputusan diambil dengan data yang benar.</li>
</ul>

<blockquote>
  <p>“Yang kita butuhkan bukan kepastian semu, melainkan keberanian untuk
  membaca data apa adanya,” ujar salah satu narasumber.</p>
</blockquote>

<h2 id="analisis">Analisis</h2>
<p>Jika pola ini berlanjut, konsekuensinya akan terasa pada
<a href="#">keputusan sehari-hari</a> banyak orang. Namun sejarah menunjukkan
bahwa tren jarang bergerak lurus; selalu ada titik balik yang sulit ditebak.</p>
<h3 id="skenario">Tiga skenario ke depan</h3>
<p>Skenario optimistis mengandaikan perbaikan tata kelola. Skenario tengah
memperkirakan status quo. Sedangkan skenario pesimistis muncul bila sinyal
peringatan terus diabaikan.</p>

<h2 id="artinya">Apa artinya bagi Anda</h2>
<p>Pada akhirnya, pembaca tidak perlu menjadi ahli untuk mengambil sikap. Yang
penting adalah memahami arah, menimbang risiko, dan tidak mudah terbawa
kegaduhan. media ini akan terus memantau perkembangan ini.</p>
`.trim();
}

export const articles: Article[] = [
  {
    id: "ev-01",
    slug: "review-byd-seal-performance-awd",
    title: "Uji Nyata BYD Seal Performance AWD: Akselerasi 3.8 Detik dan Uji Efisiensi Tol Trans Jawa",
    dek: "Kami menguji sedan listrik flagship BYD Seal bertenaga 530 PS. Seberapa irit baterai Blade 82.56 kWh saat dipacu jarak jauh?",
    cover: "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "BYD Seal melaju di jalan bebas hambatan",
    coverCaption: "Pengujian jarak jauh BYD Seal Performance AWD rute Jakarta - Semarang.",
    author: a("budi-santoso"),
    category: c("ulasan"),
    type: "premium",
    tags: [T.ev, T.baterai, T.otomotif],
    publishedAt: "2026-10-06T10:00:00+07:00",
    readingTime: 6,
    viewCount: 65420,
    isFeatured: true,
    isPinned: true,
    bodyHtml: `
<p class="lead">BYD Seal hadir sebagai salah satu sedan listrik paling dibicarakan di pasar otomotif Indonesia. Dengan banderol Rp 719 Juta untuk varian tertingginya, mobil ini menawarkan performa supercar dengan biaya operasional harian yang sangat terjangkau.</p>

<h2 id="akselerasi">Karakter Tenaga dan Akselerasi 0-100 km/j</h2>
<p>Ditenagai oleh dual motor listrik yang menyalurkan tenaga gabungan 530 PS (390 kW) dan torsi instan 670 Nm, akselerasi BYD Seal terasa sangat padat. Dalam pengujian menggunakan timing gear berbasis satelit, angka 0–100 km/j tercatat di angka 3.82 detik.</p>
<p>Sistem suspensi Frequency Selective Damping (FSD) bekerja efektif meredam hentakan, sementara teknologi CTB (Cell-to-Body) memberikan kekakuan sasis yang luar biasa saat bermanuver di tikungan kecepatan tinggi.</p>

<figure>
  <img src="https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1280&q=80" alt="Interior dan panel kemudi digital BYD Seal" width="1280" height="720" loading="lazy" />
  <figcaption>Kabin ergonomis dengan layar sentuh berputar 15.6 inci dan konsol kaca kristal.</figcaption>
</figure>

<h2 id="konsumsi">Konsumsi Daya di Tol Trans Jawa</h2>
<p>Dalam pengujian konstan pada kecepatan 100 km/j dengan AC menyala 22 derajat, konsumsi daya rata-rata berada pada angka 16.8 kWh/100 km. Baterai Blade 82.56 kWh mampu memberikan jarak tempuh riil sekitar 490 km dari klaim NEDC 580 km.</p>

<h2 id="kesimpulan">Kesimpulan Ulasan</h2>
<p>Bagi konsumen yang mendambakan kenyamanan sedan eksekutif dengan kemampuan melesat secepat sportscar, BYD Seal Performance menetapkan standar baru di segmennya.</p>
`.trim(),
  },
  {
    id: "ev-02",
    slug: "komparasi-wuling-air-ev-vs-binguo-ev",
    title: "Komparasi Wuling Air EV vs Binguo EV: Mana Mobil Listrik Paling Pas untuk Harian?",
    dek: "Membandingkan kepraktisan dimensi micro-car 3-pintu Air EV vs kenyamanan hatchback 5-pintu Binguo EV di jalanan perkotaan.",
    cover: "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "Komparasi mobil listrik kompak di area perkotaan",
    author: a("budi-santoso"),
    category: c("panduan"),
    type: "premium",
    tags: [T.ev, T.otomotif],
    publishedAt: "2026-10-05T14:30:00+07:00",
    readingTime: 5,
    viewCount: 43190,
    isFeatured: true,
    bodyHtml: `
<p class="lead">Wuling Motors menjadi pionir adopsi kendaraan listrik terjangkau di Indonesia. Kehadiran Wuling Air EV dan Binguo EV memberikan dua opsi menarik bagi konsumen perkotaan.</p>

<h2 id="dimensi">Dimensi dan Kemudahan Manuver</h2>
<p>Wuling Air EV dengan panjang 2.974 mm adalah raja manuver parkir sempit di perkotaan. Sementara itu, Binguo EV menawarkan kepraktisan 5 pintu sejati dengan ruang bagasi hingga 790 liter saat kursi baris kedua dilipat.</p>

<h2 id="baterai">Kapasitas Baterai dan Jarak Tempuh</h2>
<p>Air EV Long Range dibekali baterai 26.7 kWh (300 km CLTC), sedangkan Binguo EV Premium mengusung baterai 37.9 kWh (410 km CLTC) yang sudah mendukung DC Fast Charging GB/T.</p>
`.trim(),
  },
  {
    id: "ev-03",
    slug: "tips-merawat-baterai-mobil-listrik-lfp-nmc",
    title: "Panduan Teknis: Cara Merawat Baterai Mobil Listrik LFP vs NMC agar Awet 10 Tahun",
    dek: "Aturan pengisian 100% pada baterai LFP vs rekomendasi batas 80% pada NMC, serta pengaruh DC fast charging terhadap kesehatan sel baterai.",
    cover: "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "Port pengisian daya mobil listrik dengan indikator lampu LED",
    author: a("dimas-nugroho"),
    category: c("panduan"),
    type: "premium",
    tags: [T.baterai, T.ev],
    publishedAt: "2026-10-04T09:15:00+07:00",
    readingTime: 6,
    viewCount: 51200,
    isFeatured: true,
    bodyHtml: `
<p class="lead">Baterai traksi adalah komponen termahal pada kendaraan listrik. Memahami kimia sel baterai Anda (Lithium Iron Phosphate / LFP atau Nickel Manganese Cobalt / NMC) adalah kunci menjaga degradasi tetap minim.</p>

<h2 id="lfp-vs-nmc">Perbedaan Karakteristik Kimia</h2>
<p>Baterai LFP seperti BYD Blade Battery dan Wuling Magic Battery memiliki stabilitas termal tinggi dan aman diisi hingga 100% setiap hari untuk kalibrasi BMS (Battery Management System). Sebaliknya, sel NMC pada mobil listrik Eropa dan Korea disarankan dibatasi di 80% untuk pemakaian harian.</p>

<h2 id="fast-charging">Frekuensi Fast Charging DC</h2>
<p>Hindari melakukan DC fast charging berturut-turut saat baterai dalam kondisi suhu sangat panas. Berikan waktu istirahat 15-20 menit sebelum memulai pengisian daya super cepat.</p>
`.trim(),
  },
  {
    id: "ev-04",
    slug: "panduan-spklu-pln-fast-charging-indonesia",
    title: "Peta & Tarif SPKLU Fast Charging PLN 2026: Cara Mengisi Daya Cepat di Rest Area Tol",
    dek: "Panduan praktis menggunakan aplikasi PLN Mobile, daftar rest area dengan DC Ultra Fast Charging 200 kW, dan estimasi biaya per kWh.",
    cover: "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "Stasiun pengisian kendaraan listrik umum di rest area tol",
    author: a("budi-santoso"),
    category: c("spklu"),
    type: "premium",
    tags: [T.spklu, T.energi, T.ev],
    publishedAt: "2026-10-03T11:00:00+07:00",
    readingTime: 5,
    viewCount: 38450,
    bodyHtml: `
<p class="lead">Perjalanan darat antar-kota dengan mobil listrik kini semakin nyaman berkat sebaran stasiun pengisian kendaraan listrik umum (SPKLU) di sepanjang tol Trans Jawa dan Trans Sumatra.</p>

<h2 id="tarif">Skema Tarif Resmi Daya SPKLU</h2>
<p>Tarif pengisian daya di SPKLU PLN mengacu pada ketentuan pemerintah sebesar Rp 2.466 per kWh, ditambah biaya layanan pengisian cepat berkisar Rp 25.000 - Rp 50.000 untuk pengisian Ultra Fast Charging.</p>
`.trim(),
  },
  {
    id: "ev-05",
    slug: "insentif-ppn-1-persen-mobil-listrik-2026",
    title: "Insentif PPN 1% Mobil Listrik Resmi Berlanjut: Ini Syarat TKDN dan Daftar Model",
    dek: "Pemerintah memastikan kelanjutan pemotongan PPN dari 11% menjadi 1% bagi mobil listrik rakitan lokal (CKD) dengan TKDN minimal 40%.",
    cover: "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "Mobil listrik modern dipamerkan di pameran otomotif",
    author: a("sari-wulandari"),
    category: c("berita"),
    type: "premium",
    tags: [T.kebijakan, T.ev, T.otomotif],
    publishedAt: "2026-10-02T08:30:00+07:00",
    readingTime: 5,
    viewCount: 47800,
    bodyHtml: `
<p class="lead">Kementerian Keuangan memperpanjang fasilitas Pajak Pertambahan Nilai Ditanggung Pemerintah (PPN DTP) untuk kendaraan bermotor listrik berbasis baterai.</p>

<h2 id="syarat">Syarat Ambang Batas TKDN</h2>
<p>Model yang mendapatkan pembebasan PPN 10% (sehingga konsumen hanya membayar 1%) wajib memenuhi Tingkat Komponen Dalam Negeri (TKDN) minimal 40%, seperti Hyundai Ioniq 5, Wuling Air EV, Binguo EV, dan Chery Omoda E5.</p>
`.trim(),
  },
  {
    id: "ev-06",
    slug: "review-hyundai-ioniq-5-n",
    title: "Review Hyundai Ioniq 5 N: Monster Listrik 650 PS dengan N e-Shift Virtual",
    dek: "Mobil listrik buas yang membuktikan bahwa performa tinggi tanpa emisi bisa tetap menghadirkan keterlibatan emosional berkendara.",
    cover: "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "Hyundai Ioniq 5 N bermanuver di lintasan balap sirkuit",
    author: a("budi-santoso"),
    category: c("ulasan"),
    type: "premium",
    tags: [T.ev, T.otomotif],
    publishedAt: "2026-10-01T15:20:00+07:00",
    readingTime: 7,
    viewCount: 59300,
    bodyHtml: `
<p class="lead">Hyundai Ioniq 5 N bukan sekadar crossover bertenaga baterai; ini adalah laboratorium performa tinggi divisi N yang mendefinisikan ulang sensasi berkendara mobil listrik.</p>

<h2 id="performa">Tenaga 650 PS dan N Grin Boost</h2>
<p>Saat tombol N Grin Boost ditekan di lingkar kemudi, tenaga melonjak ke 650 PS dan torsi 770 Nm selama 10 detik penuh, melesatkan mobil dari diam ke 100 km/j dalam 3.4 detik.</p>

<h2 id="virtual-gear">N e-Shift dan N Active Sound+</h2>
<p>Inovasi paling mengagumkan adalah simulasi pergantian gigi virtual 8-percepatan yang memberikan sentakan kopling realistis serta suara mesin revving virtual.</p>
`.trim(),
  },
  {
    id: "ev-07",
    slug: "bmw-i5-touring-edrive40-m-sport-resmi-meluncur",
    title: "BMW i5 Touring eDrive40 M Sport Resmi Masuk Indonesia: Kombinasi Wagon Listrik Premium",
    dek: "BMW Group Indonesia resmi meluncurkan BMW i5 Touring seharga Rp 2.385 Miliar OTR dengan daya tempuh 560 km WLTP dan bagasi 570 liter.",
    cover: "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "BMW i5 Touring warna hitam elegan di peluncuran resmi",
    author: a("budi-santoso"),
    category: c("berita"),
    type: "premium",
    tags: [T.ev, T.otomotif],
    publishedAt: "2026-09-30T13:45:00+07:00",
    readingTime: 5,
    viewCount: 31200,
    bodyHtml: `
<p class="lead">Segmen station wagon mewah bertenaga murni listrik akhirnya resmi memiliki pionir di Indonesia melalui peluncuran BMW i5 Touring eDrive40 M Sport.</p>

<h2 id="spesifikasi">Spesifikasi Motor dan Baterai</h2>
<p>Mengusung motor listrik tunggal di poros belakang berkekuatan 340 PS dan torsi 430 Nm, i5 Touring membawa baterai berkapasitas bersih 81.2 kWh dengan jarak jangkau hingga 560 km menurut siklus WLTP.</p>
`.trim(),
  },
  {
    id: "ev-08",
    slug: "chery-j6-suv-listrik-boxy-offroad-pertama",
    title: "Chery J6 Hadir di Indonesia: SUV Listrik Boxy Tangguh dengan All-Wheel Drive",
    dek: "Chery resmi membuka babak baru di segmen SUV listrik bergaya offroad dengan meluncurkan Chery J6 berdesain maskulin dan struktur aluminium.",
    cover: "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&w=1280&q=80",
    coverAlt: "Chery J6 warna abu-abu boxy di medan offroad",
    author: a("budi-santoso"),
    category: c("berita"),
    type: "premium",
    tags: [T.ev, T.otomotif],
    publishedAt: "2026-09-29T10:10:00+07:00",
    readingTime: 5,
    viewCount: 42100,
    bodyHtml: `
<p class="lead">Chery J6 menyasar segmen penggemar petualangan outdoor yang menginginkan kendaraan listrik tangguh dengan ground clearance tinggi dan kemampuan medan offroad ringan.</p>

<h2 id="varian">Pilihan Varian RWD dan iWD AWD</h2>
<p>Tersedia dalam varian RWD Standard dan iWD Adventure AWD dengan dua motor listrik, Chery J6 mengusung baterai LFP 69.77 kWh dengan jarak tempuh hingga 501 km CLTC.</p>
`.trim(),
  },
  {
    id: "ar-01",
    slug: "arah-kebijakan-fiskal-2026",
    title: "Membaca Arah Kebijakan Fiskal 2026: Antara Ambisi dan Realita",
    dek: "Pemerintah menjanjikan belanja produktif sekaligus disiplin defisit. Bisakah keduanya berjalan beriringan tahun ini?",
    cover: cover("fiskal-2026"),
    coverAlt: "Gedung perkantoran pusat keuangan di pagi hari",
    coverCaption: "Pusat keuangan. Foto dummy untuk pratinjau.",
    author: a("sari-wulandari"),
    category: c("ekonomi"),
    type: "premium",
    tags: [T.apbn, T.kebijakan, T.inflasi],
    publishedAt: "2026-06-29T07:30:00+07:00",
    readingTime: 9,
    viewCount: 48230,
    isFeatured: true,
    isPinned: true,
    bodyHtml: buildBody(
      "Anggaran negara 2026 disusun di tengah tarik-menarik antara dorongan pertumbuhan dan tuntutan kehati-hatian fiskal.",
      "kebijakan fiskal"
    ),
  },
  {
    id: "ar-02",
    slug: "startup-lokal-musim-dingin-modal",
    title: "Startup Lokal Berburu Pendanaan di Tengah Musim Dingin Modal",
    dek: "Valuasi turun, investor lebih selektif. Para pendiri belajar bertahan dengan disiplin arus kas.",
    cover: cover("startup-funding"),
    coverAlt: "Tim startup berdiskusi di ruang kerja",
    author: a("dimas-nugroho"),
    category: c("teknologi"),
    type: "premium",
    tags: [T.startup, T.fintech],
    publishedAt: "2026-06-28T09:00:00+07:00",
    readingTime: 7,
    viewCount: 21870,
    isFeatured: true,
    bodyHtml: buildBody(
      "Era 'bakar uang' memudar. Kini metrik yang dicari investor adalah jalan menuju profitabilitas.",
      "pendanaan startup"
    ),
  },
  {
    id: "ar-03",
    slug: "ai-generatif-mengubah-ruang-redaksi",
    title: "AI Generatif Mengubah Ruang Redaksi: Peluang atau Ancaman?",
    dek: "Dari riset hingga penyuntingan, kecerdasan buatan masuk ke alur kerja jurnalis. Di mana batas yang sehat?",
    cover: cover("ai-newsroom"),
    coverAlt: "Layar komputer menampilkan teks dan grafik",
    author: a("dimas-nugroho"),
    category: c("teknologi"),
    type: "premium",
    tags: [T.ai, T.etika],
    publishedAt: "2026-06-27T16:10:00+07:00",
    readingTime: 8,
    viewCount: 33410,
    isFeatured: true,
    bodyHtml: buildBody(
      "Alih-alih menggantikan jurnalis, AI generatif menggeser definisi pekerjaan inti di ruang redaksi.",
      "AI di ruang redaksi"
    ),
  },
  {
    id: "ar-04",
    slug: "peta-koalisi-jelang-pilkada",
    title: "Peta Koalisi Menjelang Pilkada Serentak",
    dek: "Manuver partai memanas. Kami memetakan kemungkinan kombinasi dan apa risikonya bagi pemilih.",
    cover: cover("koalisi-pilkada"),
    coverAlt: "Bendera partai berderet di tepi jalan",
    author: a("rangga-pratama"),
    category: c("politik"),
    type: "premium",
    tags: [T.pemilu, T.kebijakan],
    publishedAt: "2026-06-27T08:00:00+07:00",
    readingTime: 10,
    viewCount: 29980,
    isFeatured: true,
    bodyHtml: buildBody(
      "Koalisi tidak dibentuk semalam; ia hasil dari kalkulasi elektoral yang panjang dan kadang berubah mendadak.",
      "koalisi politik"
    ),
  },
  {
    id: "ar-05",
    slug: "umkm-naik-kelas-lewat-digitalisasi-pembayaran",
    title: "UMKM Naik Kelas Lewat Digitalisasi Pembayaran",
    dek: "Bagaimana pelaku usaha kecil memanfaatkan pembayaran digital untuk memperluas pasar dan mencatat keuangan.",
    cover: cover("umkm-digital"),
    coverAlt: "Pedagang memindai kode QR pembayaran",
    author: a("sari-wulandari"),
    category: c("ekonomi"),
    type: "kerjasama",
    sponsor: {
      name: "Bank Nusantara Digital",
      website: "https://example.com",
    },
    tags: [T.umkm, T.fintech],
    publishedAt: "2026-06-26T10:30:00+07:00",
    readingTime: 6,
    viewCount: 15240,
    bodyHtml: buildBody(
      "Adopsi pembayaran digital tidak lagi soal gengsi, melainkan soal kelangsungan usaha di pasar yang kian kompetitif.",
      "digitalisasi UMKM"
    ),
  },
  {
    id: "ar-06",
    slug: "panduan-hidup-sehat-pekerja-kota",
    title: "Panduan Hidup Sehat ala Pekerja Kota",
    dek: "Jadwal padat bukan alasan mengabaikan kesehatan. Langkah kecil yang realistis untuk rutinitas harian.",
    cover: cover("sehat-kota"),
    coverAlt: "Seseorang berlari pagi di taman kota",
    author: a("ayu-lestari"),
    category: c("gaya-hidup"),
    type: "kerjasama",
    sponsor: { name: "Sehatku Clinic", website: "https://example.com" },
    tags: [T.kesehatan, T.kota],
    publishedAt: "2026-06-25T12:00:00+07:00",
    readingTime: 5,
    viewCount: 9870,
    bodyHtml: buildBody(
      "Kesehatan bukan proyek akhir pekan, melainkan akumulasi keputusan kecil yang konsisten setiap hari.",
      "hidup sehat"
    ),
  },
  {
    id: "ar-07",
    slug: "catatan-taktik-kualifikasi-timnas",
    title: "Timnas Melaju: Catatan Taktik di Babak Kualifikasi",
    dek: "Perubahan formasi dan keberanian menekan lebih awal membuahkan hasil. Apa yang berubah?",
    cover: cover("timnas-taktik"),
    coverAlt: "Pemain sepak bola di lapangan saat pertandingan",
    author: a("rangga-pratama"),
    category: c("olahraga"),
    type: "premium",
    tags: [T.timnas, T.sepakbola],
    publishedAt: "2026-06-24T22:15:00+07:00",
    readingTime: 6,
    viewCount: 41020,
    bodyHtml: buildBody(
      "Kemenangan ini bukan sekadar soal skor, tetapi tentang identitas bermain yang mulai menemukan bentuknya.",
      "taktik sepak bola"
    ),
  },
  {
    id: "ar-08",
    slug: "transparansi-anggaran-itu-penting",
    title: "Opini: Mengapa Transparansi Anggaran Itu Penting",
    dek: "Akuntabilitas dimulai dari angka yang bisa dibaca publik. Sebuah argumen untuk keterbukaan.",
    cover: cover("transparansi"),
    coverAlt: "Tumpukan dokumen dan kalkulator di meja",
    author: a("rangga-pratama"),
    category: c("opini"),
    type: "premium",
    tags: [T.kebijakan, T.apbn],
    publishedAt: "2026-06-23T11:00:00+07:00",
    readingTime: 5,
    viewCount: 12110,
    bodyHtml: buildBody(
      "Transparansi bukan beban birokrasi, melainkan fondasi kepercayaan antara negara dan warganya.",
      "transparansi anggaran"
    ),
  },
  {
    id: "ar-09",
    slug: "transisi-energi-janji-esg",
    title: "Transisi Energi: Janji ESG dan Tantangan di Lapangan",
    dek: "Komitmen hijau bertebaran di laporan tahunan. Bagaimana realisasinya di tingkat operasional?",
    cover: cover("transisi-energi"),
    coverAlt: "Turbin angin di perbukitan",
    author: a("sari-wulandari"),
    category: c("ekonomi"),
    type: "premium",
    tags: [T.esg, T.energi],
    publishedAt: "2026-06-22T08:45:00+07:00",
    readingTime: 9,
    viewCount: 18760,
    bodyHtml: buildBody(
      "Antara janji keberlanjutan dan kenyataan biaya, transisi energi menuntut lebih dari sekadar slogan.",
      "transisi energi"
    ),
  },
  {
    id: "ar-10",
    slug: "resensi-ponsel-lipat-generasi-baru",
    title: "Resensi Gawai: Ponsel Lipat Generasi Baru",
    dek: "Lebih ringan, engsel lebih kokoh, layar lebih cerah. Apakah sudah layak jadi ponsel harian?",
    cover: cover("ponsel-lipat"),
    coverAlt: "Ponsel lipat dalam posisi setengah terbuka",
    author: a("dimas-nugroho"),
    category: c("teknologi"),
    type: "kerjasama",
    sponsor: { name: "TechVerse", website: "https://example.com" },
    tags: [T.gawai],
    publishedAt: "2026-06-21T13:20:00+07:00",
    readingTime: 7,
    viewCount: 26540,
    bodyHtml: buildBody(
      "Generasi terbaru menjawab banyak keluhan lama, meski harga masih jadi penghalang utama bagi sebagian orang.",
      "ponsel lipat"
    ),
  },
  {
    id: "ar-11",
    slug: "kota-15-menit-mimpi-urban",
    title: "Kota 15 Menit: Mimpi Urban yang Mulai Nyata",
    dek: "Konsep kota yang serba dekat menarik perhatian perencana. Apa peluangnya untuk kota-kota kita?",
    cover: cover("kota-15-menit"),
    coverAlt: "Pejalan kaki di trotoar kota yang rindang",
    author: a("ayu-lestari"),
    category: c("gaya-hidup"),
    type: "premium",
    tags: [T.kota, T.kebijakan],
    publishedAt: "2026-06-20T09:30:00+07:00",
    readingTime: 6,
    viewCount: 14330,
    bodyHtml: buildBody(
      "Gagasan kota 15 menit menantang cara kita merancang ruang: dari berorientasi mobil menjadi berpusat pada manusia.",
      "perencanaan kota"
    ),
  },
  {
    id: "ar-12",
    slug: "membedah-data-inflasi",
    title: "Membedah Data Inflasi: Apa Artinya bagi Dompet Anda",
    dek: "Angka inflasi terlihat jinak, tetapi tidak semua harga bergerak sama. Ini rinciannya.",
    cover: cover("data-inflasi"),
    coverAlt: "Grafik harga pada layar dan struk belanja",
    author: a("sari-wulandari"),
    category: c("ekonomi"),
    type: "premium",
    tags: [T.inflasi, T.umkm],
    publishedAt: "2026-06-19T07:00:00+07:00",
    readingTime: 7,
    viewCount: 38990,
    bodyHtml: buildBody(
      "Rata-rata inflasi bisa menyesatkan; yang dirasakan rumah tangga sangat bergantung pada keranjang belanjanya.",
      "data inflasi"
    ),
  },
  {
    id: "ar-13",
    slug: "sepak-bola-akar-rumput",
    title: "Sepak Bola Akar Rumput dan Masa Depan Pembinaan",
    dek: "Prestasi tim nasional berakar pada pembinaan usia dini. Bagaimana kondisinya hari ini?",
    cover: cover("akar-rumput"),
    coverAlt: "Anak-anak berlatih sepak bola di lapangan desa",
    author: a("rangga-pratama"),
    category: c("olahraga"),
    type: "premium",
    tags: [T.sepakbola],
    publishedAt: "2026-06-18T15:40:00+07:00",
    readingTime: 6,
    viewCount: 11250,
    bodyHtml: buildBody(
      "Tanpa fondasi pembinaan yang kuat, prestasi sesaat sulit menjelma menjadi tradisi juara.",
      "pembinaan sepak bola"
    ),
  },
  {
    id: "ar-14",
    slug: "etika-kecerdasan-buatan",
    title: "Etika Kecerdasan Buatan: Siapa yang Bertanggung Jawab?",
    dek: "Ketika keputusan diambil oleh mesin, garis pertanggungjawaban menjadi kabur. Sebuah renungan.",
    cover: cover("etika-ai"),
    coverAlt: "Ilustrasi jaringan saraf dan figur manusia",
    author: a("dimas-nugroho"),
    category: c("opini"),
    type: "premium",
    tags: [T.ai, T.etika],
    publishedAt: "2026-06-17T10:00:00+07:00",
    readingTime: 8,
    viewCount: 16720,
    bodyHtml: buildBody(
      "Etika tidak bisa ditambahkan belakangan seperti tambalan; ia harus dirancang sejak baris pertama kode.",
      "etika AI"
    ),
  },
];
