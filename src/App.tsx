/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import {
  Search,
  ShoppingCart,
  Printer,
  FileText,
  KeyRound,
  CheckCircle2,
  AlertTriangle,
  X,
  CreditCard,
  DollarSign,
  TrendingUp,
  HelpCircle,
  Package,
  Layers,
  ArrowRight,
  Receipt,
  Trash2,
  Plus,
  Minus,
  RotateCcw,
  Clock,
  User,
  Hash,
  Database,
  Calendar,
} from 'lucide-react';

interface CartItem {
  kode: string;
  nama: string;
  harga: number;
  qty: number;
  satuan: string;
  diskon_pct: number;
  diskon_rp: number;
  is_manual?: boolean;
}

interface ProductItem {
  kode: string;
  barcode: string;
  nama: string;
  satuan: string;
  hargaBeli: number;
  hargaJual: number;
  stok: number;
}

interface PendingItem {
  id: number;
  nama_pembeli: string;
  tanggal: string;
  data: {
    keranjang: CartItem[];
    diskon_global_rp: number;
    diskon_global_persen: number;
    biaya_tambahan: number;
  };
}

interface TransaksiSelesai {
  nomor_nota: string;
  tanggal: string;
  kasir: string;
  keranjang: CartItem[];
  total: number;
  bayar: number;
  kembali: number;
  is_retur: boolean;
  diskon_global_rp: number;
  diskon_global_persen: number;
  is_copy?: boolean;
}

// Master Products matching SQLite data/toko.db
const INITIAL_PRODUCTS: ProductItem[] = [
  { kode: 'B001', barcode: '899001001', nama: 'SEMEN TIGA RODA 50KG', satuan: 'SAK', hargaBeli: 62000, hargaJual: 72000, stok: 120 },
  { kode: 'B002', barcode: '899001002', nama: 'SEMEN GRESIK 40KG', satuan: 'SAK', hargaBeli: 51000, hargaJual: 58000, stok: 85 },
  { kode: 'B003', barcode: '899001003', nama: 'BESI BETON 10MM SNI', satuan: 'BTG', hargaBeli: 72000, hargaJual: 85000, stok: 200 },
  { kode: 'B004', barcode: '899001004', nama: 'BESI BETON 8MM SNI', satuan: 'BTG', hargaBeli: 48000, hargaJual: 56000, stok: 150 },
  { kode: 'B005', barcode: '899001005', nama: 'TRIPLEK 9MM 122X244', satuan: 'LBR', hargaBeli: 115000, hargaJual: 130000, stok: 40 },
  { kode: 'B006', barcode: '899001006', nama: 'PAKU KAYU 5CM (CAMPUR)', satuan: 'KG', hargaBeli: 14000, hargaJual: 18000, stok: 50 },
  { kode: 'B007', barcode: '899001007', nama: 'PIPA PVC WAVIN 1/2 INCH D', satuan: 'BTG', hargaBeli: 22000, hargaJual: 28000, stok: 60 },
  { kode: 'B008', barcode: '899001008', nama: 'CAT TEMBOK DULUX BRILLIANT WHITE 5KG', satuan: 'GAL', hargaBeli: 135000, hargaJual: 160000, stok: 18 },
  { kode: 'B009', barcode: '899001009', nama: 'CAT BESI & KAYU AVIAN HITAM 1KG', satuan: 'KLE', hargaBeli: 58000, hargaJual: 68000, stok: 25 },
  { kode: 'B010', barcode: '899001010', nama: 'THINNER COBRA HITAM 1 LITER', satuan: 'BTL', hargaBeli: 24000, hargaJual: 30000, stok: 35 },
  { kode: 'B011', barcode: '899001011', nama: 'KUAS CAT 3 INCH ETERNA', satuan: 'PC', hargaBeli: 8500, hargaJual: 12000, stok: 45 },
  { kode: 'B012', barcode: '899001012', nama: 'KAWAT BENDRAT HITAM', satuan: 'KG', hargaBeli: 18000, hargaJual: 23000, stok: 70 },
  { kode: 'B013', barcode: '899001013', nama: 'KERAMIK MULIA 40X40 PUTIH', satuan: 'DUS', hargaBeli: 48000, hargaJual: 57000, stok: 30 },
  { kode: 'B014', barcode: '899001014', nama: 'LEM FOX KUNING 168 600GR', satuan: 'KLE', hargaBeli: 38000, hargaJual: 45000, stok: 20 },
  { kode: 'B015', barcode: '899001015', nama: 'SEAL TAPE ONDA 1/2 INCH', satuan: 'ROL', hargaBeli: 3500, hargaJual: 6000, stok: 100 }
];

export default function App() {
  // Store Config
  const namaToko = "TB.BLOTONGAN";
  const sloganToko = "TOKO BESI & BANGUNAN";
  const alamatToko = "Jl. Fatmawati 3A-B";

  // Login State
  const [isLoggedIn, setIsLoggedIn] = useState(true); // default open or can switch
  const [userId, setUserId] = useState("1");
  const [namaUser, setNamaUser] = useState("Administrator");

  // POS State
  const [keranjang, setKeranjang] = useState<CartItem[]>([
    {
      kode: 'B001',
      nama: 'SEMEN TIGA RODA 50KG',
      harga: 72000,
      qty: 2,
      satuan: 'SAK',
      diskon_pct: 0,
      diskon_rp: 0
    },
    {
      kode: 'B006',
      nama: 'PAKU KAYU 5CM (CAMPUR)',
      harga: 18000,
      qty: 1,
      satuan: 'KG',
      diskon_pct: 0,
      diskon_rp: 0
    }
  ]);
  const [selectedRowIndex, setSelectedRowIndex] = useState<number>(0);
  const [nomorNota, setNomorNota] = useState<string>("000001");
  const [shift, setShift] = useState<string>("A");
  const [nomorKassa] = useState<string>("001");
  const [inputVal, setInputVal] = useState<string>("");
  const [livePreview, setLivePreview] = useState<string>("");

  // Global discounts
  const [diskonGlobalRp, setDiskonGlobalRp] = useState<number>(0);
  const [diskonGlobalPct, setDiskonGlobalPct] = useState<number>(0);
  const [biayaTambahan, setBiayaTambahan] = useState<number>(0);
  const [memberId, setMemberId] = useState<string>("");

  // Modals state
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);
  const [showCariBarang, setShowCariBarang] = useState<boolean>(false);
  const [cariKeyword, setCariKeyword] = useState<string>("");
  const [showCheckout, setShowCheckout] = useState<boolean>(false);
  const [checkoutBayar, setCheckoutBayar] = useState<string>("");
  const [checkoutDiskonAngka, setCheckoutDiskonAngka] = useState<string>("0");
  const [checkoutDiskonPct, setCheckoutDiskonPct] = useState<string>("0");
  const [showStrukModal, setShowStrukModal] = useState<boolean>(false);
  const [strukData, setStrukData] = useState<TransaksiSelesai | null>(null);
  const [showUbahQtyModal, setShowUbahQtyModal] = useState<boolean>(false);
  const [tempQtyVal, setTempQtyVal] = useState<string>("");
  const [showDiskonItemModal, setShowDiskonItemModal] = useState<boolean>(false);
  const [tempItemDiskonPct, setTempItemDiskonPct] = useState<string>("0");
  const [tempItemDiskonRp, setTempItemDiskonRp] = useState<string>("0");
  const [showVoidModal, setShowVoidModal] = useState<boolean>(false);
  const [showOpenPluModal, setShowOpenPluModal] = useState<boolean>(false);
  const [openPluNama, setOpenPluNama] = useState<string>("BARANG");
  const [openPluHarga, setOpenPluHarga] = useState<string>("0");
  const [openPluQty, setOpenPluQty] = useState<string>("1");
  const [showPendingModal, setShowPendingModal] = useState<boolean>(false);
  const [pendingMode, setPendingMode] = useState<'save' | 'call' | 'delete'>('call');
  const [pendingName, setPendingName] = useState<string>("");
  const [pendingList, setPendingList] = useState<PendingItem[]>([]);
  const [showLaporanModal, setShowLaporanModal] = useState<boolean>(false);
  const [laporanMenu, setLaporanMenu] = useState<string>("1. Kasir - Cara Bayar");
  const [laporanTglMulai, setLaporanTglMulai] = useState<string>(new Date(Date.now() - 6 * 86400000).toISOString().split('T')[0]);
  const [laporanTglAkhir, setLaporanTglAkhir] = useState<string>(new Date().toISOString().split('T')[0]);
  const [laporanBatasan, setLaporanBatasan] = useState<'Semua' | 'Tertentu'>('Semua');
  const [laporanTertentuVal, setLaporanTertentuVal] = useState<string>('');
  const [laporanUrutan, setLaporanUrutan] = useState<'tgl' | 'faktur' | 'total'>('tgl');
  const [selectedNotaDetail, setSelectedNotaDetail] = useState<any | null>(null);

  // Phase B Seeded Data matching SQLite data/toko.db
  const [salesHistory, setSalesHistory] = useState<any[]>([
    {
      noFaktur: 'F20261102-001',
      tgl: new Date().toISOString().split('T')[0],
      jam: '08:30:15',
      kassa: '001',
      operator: 'Administrator',
      shift: 'A',
      caraBayar: 'CASH',
      total: 162000,
      dskItem: 0,
      dskGlobal: 0,
      totalVoid: 0,
      totalRefund: 0,
      items: [
        { kode: 'B001', nama: 'SEMEN TIGA RODA 50KG', qty: 2, harga: 72000, satuan: 'SAK', subtotal: 144000 },
        { kode: 'B006', nama: 'PAKU KAYU 5CM (CAMPUR)', qty: 1, harga: 18000, satuan: 'KG', subtotal: 18000 }
      ]
    },
    {
      noFaktur: 'F20261102-002',
      tgl: new Date().toISOString().split('T')[0],
      jam: '09:15:22',
      kassa: '001',
      operator: 'Administrator',
      shift: 'A',
      caraBayar: 'QRIS',
      total: 340000,
      dskItem: 10000,
      dskGlobal: 0,
      totalVoid: 0,
      totalRefund: 0,
      items: [
        { kode: 'B003', nama: 'BESI BETON 10MM SNI', qty: 4, harga: 85000, satuan: 'BTG', subtotal: 330000 },
        { kode: 'B012', nama: 'KAWAT BENDRAT HITAM', qty: 1, harga: 23000, satuan: 'KG', subtotal: 23000 }
      ]
    },
    {
      noFaktur: 'F20261102-003',
      tgl: new Date().toISOString().split('T')[0],
      jam: '10:45:00',
      kassa: '001',
      operator: 'Kasir-02',
      shift: 'A',
      caraBayar: 'DEBIT',
      total: 390000,
      dskItem: 0,
      dskGlobal: 10000,
      totalVoid: 0,
      totalRefund: 0,
      items: [
        { kode: 'B005', nama: 'TRIPLEK 9MM 122X244', qty: 3, harga: 130000, satuan: 'LBR', subtotal: 390000 },
        { kode: 'B014', nama: 'LEM FOX KUNING 168 600GR', qty: 1, harga: 45000, satuan: 'KLE', subtotal: 45000 }
      ]
    },
    {
      noFaktur: 'F20261102-004',
      tgl: new Date().toISOString().split('T')[0],
      jam: '11:20:10',
      kassa: '001',
      operator: 'Kasir-02',
      shift: 'A',
      caraBayar: 'CASH',
      total: 228000,
      dskItem: 0,
      dskGlobal: 0,
      totalVoid: 0,
      totalRefund: 0,
      items: [
        { kode: 'B008', nama: 'CAT TEMBOK DULUX BRILLIANT WHITE 5KG', qty: 1, harga: 160000, satuan: 'GAL', subtotal: 160000 },
        { kode: 'B009', nama: 'CAT BESI & KAYU AVIAN HITAM 1KG', qty: 1, harga: 68000, satuan: 'KLE', subtotal: 68000 }
      ]
    },
    {
      noFaktur: 'F20261102-005',
      tgl: new Date().toISOString().split('T')[0],
      jam: '13:05:40',
      kassa: '001',
      operator: 'Administrator',
      shift: 'B',
      caraBayar: 'TRANSFER',
      total: 570000,
      dskItem: 0,
      dskGlobal: 0,
      totalVoid: 0,
      totalRefund: 0,
      items: [
        { kode: 'B013', nama: 'KERAMIK MULIA 40X40 PUTIH', qty: 10, harga: 57000, satuan: 'DUS', subtotal: 570000 }
      ]
    },
    {
      noFaktur: 'F20261102-006',
      tgl: new Date().toISOString().split('T')[0],
      jam: '14:22:15',
      kassa: '001',
      operator: 'Administrator',
      shift: 'B',
      caraBayar: 'CASH',
      total: 114000,
      dskItem: 0,
      dskGlobal: 0,
      totalVoid: 0,
      totalRefund: 56000,
      items: [
        { kode: 'B004', nama: 'BESI BETON 8MM SNI', qty: 3, harga: 56000, satuan: 'BTG', subtotal: 168000 },
        { kode: 'B004', nama: 'BESI BETON 8MM SNI (RETUR)', qty: -1, harga: 56000, satuan: 'BTG', subtotal: -56000, isRetur: true }
      ]
    },
    {
      noFaktur: 'F20261101-001',
      tgl: new Date(Date.now() - 86400000).toISOString().split('T')[0],
      jam: '15:10:00',
      kassa: '001',
      operator: 'Administrator',
      shift: 'A',
      caraBayar: 'CASH',
      total: 288000,
      dskItem: 0,
      dskGlobal: 0,
      totalVoid: 0,
      totalRefund: 0,
      items: [
        { kode: 'B001', nama: 'SEMEN TIGA RODA 50KG', qty: 4, harga: 72000, satuan: 'SAK', subtotal: 288000 }
      ]
    }
  ]);

  // Phase B Shift Reconciliations matching SQLite kasir table
  const [shiftHistory] = useState<any[]>([
    { kassa: '001', operator: 'Administrator', shift: 'A', tanggal: new Date().toISOString().split('T')[0], modal: 200000, biaya: 15000, totalJual: 502000, setoran: 687000 },
    { kassa: '001', operator: 'Kasir-02', shift: 'A', tanggal: new Date().toISOString().split('T')[0], modal: 200000, biaya: 0, totalJual: 618000, setoran: 818000 },
    { kassa: '001', operator: 'Administrator', shift: 'B', tanggal: new Date().toISOString().split('T')[0], modal: 200000, biaya: 25000, totalJual: 684000, setoran: 859000 }
  ]);

  const [transaksiTerakhir, setTransaksiTerakhir] = useState<TransaksiSelesai | null>(null);
  const [notifMessage, setNotifMessage] = useState<{ title: string; text: string; type: 'info' | 'error' | 'success' } | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  // Formatter
  const formatRp = (num: number) => {
    return `Rp ${Math.round(num).toLocaleString('id-ID')}`;
  };

  // Calculations
  const subtotalKeranjang = keranjang.reduce((sum, item) => {
    const potPct = (item.harga * (item.diskon_pct || 0)) / 100;
    const sub = (item.harga - potPct) * item.qty - (item.diskon_rp || 0);
    return sum + sub;
  }, 0);

  const totalQty = keranjang.reduce((sum, item) => sum + item.qty, 0);

  const grandTotal = Math.max(
    0,
    subtotalKeranjang - diskonGlobalRp - (subtotalKeranjang * diskonGlobalPct) / 100 + biayaTambahan
  );

  // Live input preview
  useEffect(() => {
    const q = inputVal.trim();
    if (!q) {
      setLivePreview("");
      return;
    }
    const parts = q.split(" ");
    const kode = parts[0];
    const qty = parts.length >= 2 ? parseFloat(parts[1]) || 1 : 1;

    const matched = INITIAL_PRODUCTS.find(
      (p) => p.kode.toLowerCase() === kode.toLowerCase() || p.barcode === kode || p.nama.toLowerCase().includes(kode.toLowerCase())
    );

    if (matched) {
      setLivePreview(`⟳ ${matched.nama} × ${qty} ${matched.satuan} = ${formatRp(matched.hargaJual * qty)}`);
    } else {
      setLivePreview(`⟳ Kode / nama '${q}' belum terdaftar (tekan F10 untuk cari)`);
    }
  }, [inputVal]);

  // Input barcode submit
  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const val = inputVal.trim();
    if (!val) return;

    // Check if user typed negative number to change current selected row qty directly
    if (val.startsWith("-") && !isNaN(Number(val))) {
      const num = parseFloat(val);
      if (selectedRowIndex >= 0 && selectedRowIndex < keranjang.length) {
        const next = [...keranjang];
        next[selectedRowIndex].qty = num;
        setKeranjang(next);
        setInputVal("");
        return;
      }
    }

    const parts = val.split(" ");
    const kode = parts[0];
    const qty = parts.length >= 2 ? parseFloat(parts[1]) || 1 : 1;

    const matched = INITIAL_PRODUCTS.find(
      (p) => p.kode.toLowerCase() === kode.toLowerCase() || p.barcode === kode
    );

    if (matched) {
      tambahItem(matched.kode, matched.nama, matched.hargaJual, qty, matched.satuan);
      setInputVal("");
    } else {
      // If not exact, open F10 dialog with initial keyword
      setCariKeyword(val);
      setShowCariBarang(true);
      setInputVal("");
    }
  };

  const tambahItem = (kode: string, nama: string, harga: number, qty = 1, satuan = "PC") => {
    setKeranjang((prev) => {
      const idx = prev.findIndex((i) => i.kode === kode);
      if (idx !== -1) {
        const updated = [...prev];
        updated[idx].qty += qty;
        setSelectedRowIndex(idx);
        return updated;
      } else {
        const next = [...prev, { kode, nama, harga, qty, satuan, diskon_pct: 0, diskon_rp: 0 }];
        setSelectedRowIndex(next.length - 1);
        return next;
      }
    });
  };

  // Keyboard Hotkeys listener (matching Windows POS Tkinter keys)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // If modal is open and Esc pressed, close modal
      if (e.key === "Escape") {
        if (showCariBarang || showCheckout || showStrukModal || showUbahQtyModal || showDiskonItemModal || showVoidModal || showOpenPluModal || showPendingModal || showLaporanModal || showLoginModal || notifMessage) {
          setShowCariBarang(false);
          setShowCheckout(false);
          setShowStrukModal(false);
          setShowUbahQtyModal(false);
          setShowDiskonItemModal(false);
          setShowVoidModal(false);
          setShowOpenPluModal(false);
          setShowPendingModal(false);
          setShowLaporanModal(false);
          setShowLoginModal(false);
          setNotifMessage(null);
          e.preventDefault();
          inputRef.current?.focus();
          return;
        }
      }

      // Hotkey F1: Bantuan
      if (e.key === "F1") {
        e.preventDefault();
        setNotifMessage({
          title: "BANTUAN HOTKEY POS",
          text: "[F1] Bantuan | [F2] Void | [F3] Open PLU | [F4] Ubah Harga | [F5] Simpan Pending | [F6] Panggil Pending | [F7] Hapus Pending | [F8] Laporan | [F9] Diskon Item | [F10] Cari Barang | [+] Checkout | [*] Ubah Qty | [-] Retur | [F11] Laci | [F12] Copy Struk",
          type: "info"
        });
      }

      // Hotkey F2: Void Item
      if (e.key === "F2") {
        e.preventDefault();
        if (keranjang.length > 0) setShowVoidModal(true);
      }

      // Hotkey F3: Open PLU
      if (e.key === "F3") {
        e.preventDefault();
        setShowOpenPluModal(true);
      }

      // Hotkey F5: Simpan Pending
      if (e.key === "F5") {
        e.preventDefault();
        if (keranjang.length === 0) {
          setNotifMessage({ title: "Perhatian", text: "Keranjang masih kosong!", type: "info" });
        } else {
          setPendingMode('save');
          setShowPendingModal(true);
        }
      }

      // Hotkey F6: Panggil Pending
      if (e.key === "F6") {
        e.preventDefault();
        setPendingMode('call');
        setShowPendingModal(true);
      }

      // Hotkey F7: Hapus Pending
      if (e.key === "F7") {
        e.preventDefault();
        setPendingMode('delete');
        setShowPendingModal(true);
      }

      // Hotkey F8: Laporan
      if (e.key === "F8") {
        e.preventDefault();
        setShowLaporanModal(true);
      }

      // Hotkey F9: Diskon Item
      if (e.key === "F9") {
        e.preventDefault();
        if (keranjang.length > 0 && selectedRowIndex >= 0) {
          const item = keranjang[selectedRowIndex];
          setTempItemDiskonPct(String(item.diskon_pct || 0));
          setTempItemDiskonRp(String(item.diskon_rp || 0));
          setShowDiskonItemModal(true);
        }
      }

      // Hotkey F10: Cari Barang
      if (e.key === "F10") {
        e.preventDefault();
        setShowCariBarang(true);
      }

      // Hotkey F11: Buka Laci
      if (e.key === "F11") {
        e.preventDefault();
        setNotifMessage({ title: "Buka Laci Kasir", text: "Sinyal pembuka laci kasir (Cash Drawer ESC/POS) berhasil dikirim!", type: "success" });
      }

      // Hotkey F12: Copy Struk Terakhir
      if (e.key === "F12") {
        e.preventDefault();
        if (transaksiTerakhir) {
          setStrukData({ ...transaksiTerakhir, is_copy: true });
          setShowStrukModal(true);
        } else {
          setNotifMessage({ title: "Info", text: "Belum ada transaksi sebelumnya untuk dicetak ulang.", type: "info" });
        }
      }

      // Hotkey + : Checkout
      if (e.key === "+" && document.activeElement !== inputRef.current) {
        e.preventDefault();
        if (keranjang.length > 0) {
          setCheckoutBayar("");
          setShowCheckout(true);
        }
      }

      // Hotkey * : Ubah Qty Item
      if (e.key === "*" && document.activeElement !== inputRef.current) {
        e.preventDefault();
        if (keranjang.length > 0 && selectedRowIndex >= 0) {
          setTempQtyVal(String(keranjang[selectedRowIndex].qty));
          setShowUbahQtyModal(true);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [keranjang, selectedRowIndex, showCariBarang, showCheckout, showStrukModal, showUbahQtyModal, showDiskonItemModal, showVoidModal, showOpenPluModal, showPendingModal, showLaporanModal, showLoginModal, notifMessage, transaksiTerakhir]);

  // Execute checkout
  const handleProsesCheckout = () => {
    const bayarNum = parseFloat(checkoutBayar.replace(/\./g, '')) || 0;
    const diskonRp = parseFloat(checkoutDiskonAngka.replace(/\./g, '')) || 0;
    const diskonPct = parseFloat(checkoutDiskonPct) || 0;
    const totalAkhir = Math.max(0, subtotalKeranjang - diskonRp - (subtotalKeranjang * diskonPct) / 100);

    if (bayarNum < totalAkhir) {
      setNotifMessage({ title: "Error", text: "Nominal pembayaran masih kurang!", type: "error" });
      return;
    }

    const kembaliNum = bayarNum - totalAkhir;
    const tx: TransaksiSelesai = {
      nomor_nota: nomorNota,
      tanggal: new Date().toLocaleString('id-ID'),
      kasir: namaUser,
      keranjang: [...keranjang],
      total: totalAkhir,
      bayar: bayarNum,
      kembali: kembaliNum,
      is_retur: false,
      diskon_global_rp: diskonRp,
      diskon_global_persen: diskonPct,
    };

    setTransaksiTerakhir(tx);
    setStrukData(tx);
    setShowCheckout(false);
    setShowStrukModal(true);

    // Tambah ke riwayat transaksi untuk sinkronisasi live laporan
    const txRecord = {
      noFaktur: `F${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${nomorNota}`,
      tgl: new Date().toISOString().split('T')[0],
      jam: new Date().toLocaleTimeString('id-ID'),
      kassa: nomorKassa,
      operator: namaUser,
      shift: shift,
      caraBayar: 'CASH',
      total: totalAkhir,
      dskItem: keranjang.reduce((sum, itm) => sum + (itm.diskon_rp || 0), 0),
      dskGlobal: diskonRp,
      totalVoid: 0,
      totalRefund: 0,
      items: keranjang.map((i) => ({
        kode: i.kode,
        nama: i.nama,
        qty: i.qty,
        harga: i.harga,
        satuan: i.satuan,
        subtotal: (i.harga - (i.harga * (i.diskon_pct || 0) / 100)) * i.qty - (i.diskon_rp || 0)
      }))
    };
    setSalesHistory((prev) => [txRecord, ...prev]);

    // Reset keranjang
    setKeranjang([]);
    setDiskonGlobalRp(0);
    setDiskonGlobalPct(0);
    setNomorNota((prev) => String(parseInt(prev) + 1).padStart(6, '0'));

    try {
      confetti({ particleCount: 35, spread: 60, origin: { y: 0.8 } });
    } catch {}
  };

  return (
    <div className="min-h-screen bg-[#1E1E2E] text-[#F8F8F2] flex flex-col font-sans select-none overflow-hidden text-xs sm:text-sm">
      {/* 1. HEADER - Matching ui/main_window.py */}
      <header className="bg-[#1E1E2E] border-b border-[#161622] px-4 py-2.5 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#4F46E5] flex items-center justify-center font-bold text-white shadow">
            TB
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-[#F8F8F2]">
                ◉ KASSA {nomorKassa} · {namaToko}
              </span>
              <span className="text-[11px] font-semibold text-[#50FA7B] bg-[#50FA7B]/10 px-2 py-0.5 rounded-full border border-[#50FA7B]/20">
                ● ONLINE
              </span>
            </div>
            <p className="text-[11px] text-[#A0A5B5]">{sloganToko} · {alamatToko}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowLaporanModal(true)}
            className="px-3 py-1.5 bg-[#282A36] hover:bg-[#343746] text-[#A0A5B5] hover:text-[#F8F8F2] rounded-lg border border-[#343746] text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <TrendingUp className="w-3.5 h-3.5 text-[#4F46E5]" />
            <span>[F8] Laporan</span>
          </button>

          <button
            onClick={() => {
              setPendingMode('call');
              setShowPendingModal(true);
            }}
            className="px-3 py-1.5 bg-[#282A36] hover:bg-[#343746] text-[#A0A5B5] hover:text-[#F8F8F2] rounded-lg border border-[#343746] text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Layers className="w-3.5 h-3.5 text-[#F7AD31]" />
            <span>Pending ({pendingList.length})</span>
          </button>

          <button
            onClick={() => setShowLoginModal(true)}
            className="px-3 py-1.5 bg-[#4F46E5] hover:bg-[#6366F1] text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow transition-colors"
          >
            <User className="w-3.5 h-3.5" />
            <span>{namaUser}</span>
          </button>
        </div>
      </header>

      {/* 2. INFO BAR & QTY BAR */}
      <div className="bg-[#1E1E2E] px-4 py-2 border-b border-[#282A36] flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-4 text-[#A0A5B5]">
          <span className="text-[#4F46E5] font-semibold flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            {new Date().toLocaleDateString('id-ID', { day: '2-digit', month: '2-digit', year: 'numeric' })}
          </span>
          <span>·</span>
          <span>Shift: <strong className="text-[#F8F8F2]">{shift}</strong></span>
          <span>·</span>
          <span>Operator: <strong className="text-[#F8F8F2]">{namaUser}</strong></span>
          <span>·</span>
          <span>Pelanggan: <strong className="text-[#F8F8F2]">UMUM</strong></span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-[#4F46E5] font-mono font-bold text-xs bg-[#282A36] px-3 py-1 rounded border border-[#343746]">
            TOTAL QTY: {totalQty.toFixed(2)}
          </span>
          <span className="text-[#F7AD31] font-mono font-bold text-xs bg-[#282A36] px-3 py-1 rounded border border-[#343746]">
            NOTA: {nomorNota}
          </span>
        </div>
      </div>

      {/* 3. MAIN KERANJANG TABLE */}
      <div className="flex-1 overflow-y-auto px-4 py-2">
        <div className="bg-[#282A36] rounded-xl border border-[#343746] shadow-md overflow-hidden">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-[#191A21] text-[#4F46E5] font-mono uppercase font-bold tracking-wider border-b border-[#343746] text-[11px]">
                <th className="py-2.5 px-3 text-center w-12">NO</th>
                <th className="py-2.5 px-3 text-center w-24">KODE</th>
                <th className="py-2.5 px-4">NAMA BARANG</th>
                <th className="py-2.5 px-3 text-right w-28">HARGA</th>
                <th className="py-2.5 px-3 text-center w-24">DISKON %</th>
                <th className="py-2.5 px-3 text-center w-28">QTY</th>
                <th className="py-2.5 px-4 text-right w-36">SUBTOTAL</th>
              </tr>
            </thead>
            <tbody className="font-mono divide-y divide-[#343746]/50">
              {keranjang.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center text-[#A0A5B5]">
                    <ShoppingCart className="w-10 h-10 mx-auto stroke-1 opacity-30 mb-2" />
                    <p className="font-semibold text-sm">Keranjang Transaksi Kosong</p>
                    <p className="text-xs text-[#A0A5B5] mt-1">
                      Ketik kode barang / nama di bawah atau tekan <span className="text-[#4F46E5] font-bold">[F10] Cari Barang</span>.
                    </p>
                  </td>
                </tr>
              ) : (
                keranjang.map((item, idx) => {
                  const potPct = (item.harga * (item.diskon_pct || 0)) / 100;
                  const lineSubtotal = (item.harga - potPct) * item.qty - (item.diskon_rp || 0);
                  const isSelected = selectedRowIndex === idx;

                  return (
                    <tr
                      key={idx}
                      onClick={() => setSelectedRowIndex(idx)}
                      className={`cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-[#44475A] text-white font-bold'
                          : idx % 2 === 0
                          ? 'bg-[#282A36] text-[#F8F8F2] hover:bg-[#343746]'
                          : 'bg-[#222430] text-[#F8F8F2] hover:bg-[#343746]'
                      } ${item.qty < 0 ? 'text-[#FF5555]' : ''}`}
                    >
                      <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{idx + 1}</td>
                      <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{item.kode}</td>
                      <td className="py-2.5 px-4 font-sans font-semibold truncate max-w-md">
                        {item.nama}
                      </td>
                      <td className="py-2.5 px-3 text-right">{item.harga.toLocaleString('id-ID')}</td>
                      <td className="py-2.5 px-3 text-center text-[#F7AD31]">
                        {item.diskon_pct > 0 ? `${item.diskon_pct}%` : item.diskon_rp > 0 ? `-${item.diskon_rp.toLocaleString('id-ID')}` : '-'}
                      </td>
                      <td className="py-2.5 px-3 text-center font-bold">
                        {item.qty} {item.satuan}
                      </td>
                      <td className="py-2.5 px-4 text-right font-extrabold text-[#50FA7B]">
                        {lineSubtotal.toLocaleString('id-ID')}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. FOOTER: JUMLAH TOTAL & LIVE PREVIEW */}
      <div className="bg-[#282A36] border-t border-[#343746] px-5 py-3 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Live Preview Bar */}
          <div className="text-xs text-[#50FA7B] font-mono h-5 truncate">
            {livePreview || "  ⟳ Ketik kode barang atau tekan F10 untuk cari..."}
          </div>

          {/* Grand Total */}
          <div className="flex items-center gap-3 self-end md:self-auto">
            <span className="font-bold text-sm text-[#A0A5B5]">JUMLAH :</span>
            <div className="font-mono text-3xl font-extrabold text-[#50FA7B] tracking-tight">
              {formatRp(grandTotal)}
            </div>
          </div>
        </div>
      </div>

      {/* 5. INPUT BAR & HOTKEY CONTROLS */}
      <div className="bg-[#1E1E2E] border-t border-[#282A36] p-3 space-y-2.5">
        <form onSubmit={handleInputSubmit} className="flex items-center gap-2">
          <div className="relative flex-1">
            <span className="absolute left-3.5 top-3 text-[#4F46E5] font-bold text-sm">
              🔍 INPUT:
            </span>
            <input
              ref={inputRef}
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ketik kode / barcode / nama barang lalu tekan ENTER..."
              className="w-full bg-[#1E1E2E] text-[#F8F8F2] text-sm pl-24 pr-4 py-2.5 rounded-xl border-2 border-[#4F46E5] focus:outline-none focus:ring-2 focus:ring-[#6366F1] font-mono shadow-inner"
              autoFocus
            />
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 bg-[#4F46E5] hover:bg-[#6366F1] text-white rounded-xl font-bold text-xs shadow-md transition-colors shrink-0"
          >
            ENTER
          </button>

          <button
            type="button"
            onClick={() => {
              if (keranjang.length > 0) {
                setCheckoutBayar("");
                setShowCheckout(true);
              }
            }}
            disabled={keranjang.length === 0}
            className="px-6 py-2.5 bg-[#50FA7B] hover:bg-[#40e06a] text-[#1E1E2E] font-extrabold text-sm rounded-xl shadow-md transition-all shrink-0 disabled:opacity-40"
          >
            [+] BAYAR
          </button>
        </form>

        {/* Hotkeys Buttons Row */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px] overflow-x-auto pb-1 text-[#A0A5B5]">
          <button
            onClick={() => setNotifMessage({ title: "BANTUAN HOTKEY POS", text: "[F1] Bantuan | [F2] Void | [F3] Open PLU | [F4] Ubah Harga | [F5] Simpan Pending | [F6] Panggil Pending | [F7] Hapus Pending | [F8] Laporan | [F9] Diskon Item | [F10] Cari Barang | [+] Checkout | [*] Ubah Qty | [-] Retur | [F11] Laci | [F12] Copy Struk", type: "info" })}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F8F8F2]"
          >
            [F1] Bantuan
          </button>

          <button
            onClick={() => { if (keranjang.length > 0) setShowVoidModal(true); }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#FF5555]"
          >
            [F2] Void
          </button>

          <button
            onClick={() => setShowOpenPluModal(true)}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F8F8F2]"
          >
            [F3] Open PLU
          </button>

          <button
            onClick={() => {
              if (keranjang.length > 0 && selectedRowIndex >= 0) {
                const item = keranjang[selectedRowIndex];
                const newPriceStr = prompt(`Ubah Harga untuk ${item.nama}:`, String(item.harga));
                if (newPriceStr) {
                  const p = parseFloat(newPriceStr.replace(/\./g, ''));
                  if (!isNaN(p) && p >= 0) {
                    const next = [...keranjang];
                    next[selectedRowIndex].harga = p;
                    setKeranjang(next);
                  }
                }
              }
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F8F8F2]"
          >
            [F4] Ubah Harga
          </button>

          <button
            onClick={() => {
              if (keranjang.length > 0) {
                setPendingMode('save');
                setShowPendingModal(true);
              }
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F7AD31]"
          >
            [F5] Simpan Pending
          </button>

          <button
            onClick={() => {
              setPendingMode('call');
              setShowPendingModal(true);
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F8F8F2]"
          >
            [F6] Panggil
          </button>

          <button
            onClick={() => {
              setPendingMode('delete');
              setShowPendingModal(true);
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#A0A5B5]"
          >
            [F7] Hapus Pending
          </button>

          <button
            onClick={() => setShowLaporanModal(true)}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#50FA7B]"
          >
            [F8] Laporan
          </button>

          <button
            onClick={() => {
              if (keranjang.length > 0 && selectedRowIndex >= 0) {
                const item = keranjang[selectedRowIndex];
                setTempItemDiskonPct(String(item.diskon_pct || 0));
                setTempItemDiskonRp(String(item.diskon_rp || 0));
                setShowDiskonItemModal(true);
              }
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F7AD31]"
          >
            [F9] Diskon Item
          </button>

          <button
            onClick={() => setShowCariBarang(true)}
            className="px-2 py-1 bg-[#4F46E5] text-white rounded font-bold"
          >
            [F10] Cari Barang
          </button>

          <button
            onClick={() => {
              if (keranjang.length > 0 && selectedRowIndex >= 0) {
                setTempQtyVal(String(keranjang[selectedRowIndex].qty));
                setShowUbahQtyModal(true);
              }
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#F8F8F2]"
          >
            [*] Ubah Qty
          </button>

          <button
            onClick={() => {
              if (keranjang.length > 0 && selectedRowIndex >= 0) {
                const next = [...keranjang];
                next[selectedRowIndex].qty = -Math.abs(next[selectedRowIndex].qty);
                setKeranjang(next);
              }
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#FF5555]"
          >
            [-] Retur
          </button>

          <button
            onClick={() => setNotifMessage({ title: "Buka Laci", text: "Perintah buka laci kasir (Drawer ESC/POS) berhasil dikirim.", type: "success" })}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#A0A5B5]"
          >
            [F11] Laci
          </button>

          <button
            onClick={() => {
              if (transaksiTerakhir) {
                setStrukData({ ...transaksiTerakhir, is_copy: true });
                setShowStrukModal(true);
              } else {
                setNotifMessage({ title: "Info", text: "Belum ada transaksi terakhir untuk dicetak ulang.", type: "info" });
              }
            }}
            className="px-2 py-1 bg-[#282A36] hover:bg-[#343746] rounded border border-[#343746] text-[#4F46E5]"
          >
            [F12] Copy Struk
          </button>
        </div>
      </div>

      {/* ============================================================ */}
      {/* MODAL: F10 CARI DATA BARANG (Matching handlers/cari_barang.py) */}
      {/* ============================================================ */}
      {showCariBarang && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-4xl w-full border border-[#4F46E5] shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            <div className="p-3 bg-[#1E1E2E] text-[#F8F8F2] font-bold text-sm flex items-center justify-between border-b border-[#343746]">
              <span>◉ CARI DATA BARANG · ESC untuk keluar</span>
              <button onClick={() => setShowCariBarang(false)} className="text-[#A0A5B5] hover:text-white">✕</button>
            </div>

            <div className="p-4 bg-[#282A36] border-b border-[#343746] flex items-center gap-3">
              <span className="text-[#4F46E5] font-bold text-xs">🔍 DICARI :</span>
              <input
                type="text"
                value={cariKeyword}
                onChange={(e) => setCariKeyword(e.target.value)}
                placeholder="Ketik nama barang / kode / barcode..."
                className="flex-1 bg-[#1E1E2E] text-[#F8F8F2] text-sm px-3 py-2 rounded-lg border border-[#4F46E5] focus:outline-none"
                autoFocus
              />
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-[#4F46E5] font-mono border-b border-[#343746] pb-2">
                    <th className="py-2 px-2 text-center">PLU</th>
                    <th className="py-2 px-2 text-center">BARCODE</th>
                    <th className="py-2 px-4">NAMA BARANG</th>
                    <th className="py-2 px-3 text-right">HARGA JUAL</th>
                    <th className="py-2 px-2 text-center">SATUAN</th>
                    <th className="py-2 px-3 text-right">STOK</th>
                    <th className="py-2 px-3 text-center">AKSI</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#343746]/50 font-mono">
                  {INITIAL_PRODUCTS.filter((p) => {
                    const q = cariKeyword.toLowerCase();
                    return p.nama.toLowerCase().includes(q) || p.kode.toLowerCase().includes(q) || p.barcode.includes(q);
                  }).map((p) => (
                    <tr key={p.kode} className="hover:bg-[#343746] transition-colors">
                      <td className="py-2 px-2 text-center text-[#A0A5B5]">{p.kode}</td>
                      <td className="py-2 px-2 text-center text-[#A0A5B5]">{p.barcode}</td>
                      <td className="py-2 px-4 font-sans font-semibold text-[#F8F8F2]">{p.nama}</td>
                      <td className="py-2 px-3 text-right text-[#50FA7B] font-bold">{formatRp(p.hargaJual)}</td>
                      <td className="py-2 px-2 text-center text-[#A0A5B5]">{p.satuan}</td>
                      <td className={`py-2 px-3 text-right font-bold ${p.stok <= 10 ? 'text-[#FF5555]' : 'text-[#F8F8F2]'}`}>{p.stok}</td>
                      <td className="py-2 px-3 text-center">
                        <button
                          onClick={() => {
                            tambahItem(p.kode, p.nama, p.hargaJual, 1, p.satuan);
                            setShowCariBarang(false);
                          }}
                          className="px-2.5 py-1 bg-[#4F46E5] hover:bg-[#6366F1] text-white rounded font-bold text-[11px]"
                        >
                          + Pilih
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [+] CHECKOUT & PEMBAYARAN (Matching handlers/checkout.py) */}
      {/* ============================================================ */}
      {showCheckout && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-lg w-full border border-[#4F46E5] shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#343746]">
              <h3 className="font-bold text-base text-[#F7AD31]">PEMBAYARAN KASIR</h3>
              <button onClick={() => setShowCheckout(false)} className="text-[#A0A5B5] hover:text-white">✕</button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center bg-[#1E1E2E] p-3 rounded-xl border border-[#343746]">
                <span className="font-bold text-sm text-[#A0A5B5]">TOTAL TAGIHAN:</span>
                <span className="font-mono text-2xl font-extrabold text-[#F7AD31]">{formatRp(subtotalKeranjang)}</span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A0A5B5] font-semibold mb-1">Diskon Angka (F4 Rp):</label>
                  <input
                    type="number"
                    value={checkoutDiskonAngka}
                    onChange={(e) => setCheckoutDiskonAngka(e.target.value)}
                    className="w-full bg-[#1E1E2E] text-[#4F46E5] font-bold p-2 rounded-lg border border-[#343746]"
                  />
                </div>
                <div>
                  <label className="block text-[#A0A5B5] font-semibold mb-1">Diskon Persen (F5 %):</label>
                  <input
                    type="number"
                    value={checkoutDiskonPct}
                    onChange={(e) => setCheckoutDiskonPct(e.target.value)}
                    className="w-full bg-[#1E1E2E] text-[#4F46E5] font-bold p-2 rounded-lg border border-[#343746]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[#A0A5B5] font-semibold mb-1">Pembayaran Diterima (Rp) *</label>
                <input
                  type="number"
                  value={checkoutBayar}
                  onChange={(e) => setCheckoutBayar(e.target.value)}
                  placeholder="Masukkan uang pembeli..."
                  className="w-full bg-[#1E1E2E] text-[#50FA7B] font-mono text-xl font-bold p-2.5 rounded-lg border-2 border-[#50FA7B] focus:outline-none"
                  autoFocus
                />
              </div>

              {/* Quick Cash Buttons */}
              <div className="flex flex-wrap gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setCheckoutBayar(String(grandTotal))}
                  className="px-2.5 py-1 bg-[#343746] hover:bg-[#44475A] rounded text-[11px] font-bold text-[#F8F8F2]"
                >
                  Uang Pas
                </button>
                <button
                  type="button"
                  onClick={() => setCheckoutBayar("50000")}
                  className="px-2.5 py-1 bg-[#343746] hover:bg-[#44475A] rounded text-[11px] font-bold text-[#F8F8F2]"
                >
                  50.000
                </button>
                <button
                  type="button"
                  onClick={() => setCheckoutBayar("100000")}
                  className="px-2.5 py-1 bg-[#343746] hover:bg-[#44475A] rounded text-[11px] font-bold text-[#F8F8F2]"
                >
                  100.000
                </button>
                <button
                  type="button"
                  onClick={() => setCheckoutBayar("200000")}
                  className="px-2.5 py-1 bg-[#343746] hover:bg-[#44475A] rounded text-[11px] font-bold text-[#F8F8F2]"
                >
                  200.000
                </button>
                <button
                  type="button"
                  onClick={() => setCheckoutBayar("500000")}
                  className="px-2.5 py-1 bg-[#343746] hover:bg-[#44475A] rounded text-[11px] font-bold text-[#F8F8F2]"
                >
                  500.000
                </button>
              </div>

              {/* Kembalian calculation */}
              <div className="p-3 bg-[#1E1E2E] rounded-xl border border-[#343746] flex items-center justify-between">
                <span className="font-semibold text-xs text-[#A0A5B5]">KEMBALIAN:</span>
                <span className={`font-mono text-2xl font-extrabold ${
                  (parseFloat(checkoutBayar) || 0) >= grandTotal ? 'text-[#50FA7B]' : 'text-[#FF5555]'
                }`}>
                  {formatRp(Math.max(0, (parseFloat(checkoutBayar) || 0) - grandTotal))}
                </span>
              </div>
            </div>

            <div className="flex gap-2 justify-end pt-3 border-t border-[#343746]">
              <button
                type="button"
                onClick={() => setShowCheckout(false)}
                className="px-4 py-2 bg-[#343746] hover:bg-[#44475A] rounded-xl text-xs font-semibold text-[#F8F8F2]"
              >
                Batal (ESC)
              </button>
              <button
                type="button"
                onClick={handleProsesCheckout}
                className="px-6 py-2 bg-[#4F46E5] hover:bg-[#6366F1] text-white rounded-xl text-xs font-bold shadow transition-all"
              >
                PROSES PEMBAYARAN (ENTER)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: STRUK THERMAL (Matching handlers/print_struk.py) */}
      {/* ============================================================ */}
      {showStrukModal && strukData && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-sm w-full border border-[#4F46E5] shadow-2xl p-5 space-y-4 max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between pb-2 border-b border-[#343746]">
              <span className="font-bold text-xs text-[#50FA7B]">STRUK THERMAL ESC/POS</span>
              <button onClick={() => setShowStrukModal(false)} className="text-[#A0A5B5] hover:text-white">✕</button>
            </div>

            <div className="bg-white text-black p-4 rounded font-mono text-[11px] leading-tight select-all overflow-y-auto">
              <div className="text-center font-bold">
                ================================<br />
                {namaToko}<br />
                {sloganToko}<br />
                {alamatToko}<br />
                ================================<br />
              </div>
              {strukData.is_copy && (
                <div className="text-center font-bold text-red-600">
                  *** COPY STRUK ***<br />
                </div>
              )}
              <div>
                No   : {strukData.nomor_nota}<br />
                Tgl  : {strukData.tanggal}<br />
                Kasir: {strukData.kasir}<br />
                --------------------------------<br />
              </div>
              <div className="space-y-1">
                {strukData.keranjang.map((item, i) => (
                  <div key={i}>
                    <div>{item.nama}</div>
                    <div className="flex justify-between">
                      <span>  {item.qty} x Rp {item.harga.toLocaleString('id-ID')}</span>
                      <span>Rp {(item.harga * item.qty).toLocaleString('id-ID')}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div>
                --------------------------------<br />
                <div className="flex justify-between font-bold">
                  <span>TOTAL:</span>
                  <span>Rp {strukData.total.toLocaleString('id-ID')}</span>
                </div>
                <div className="flex justify-between">
                  <span>BAYAR:</span>
                  <span>Rp {strukData.bayar.toLocaleString('id-ID')}</span>
                </div>
                <div className="flex justify-between font-bold">
                  <span>KEMBALI:</span>
                  <span>Rp {strukData.kembali.toLocaleString('id-ID')}</span>
                </div>
                ================================<br />
                <div className="text-center text-[10px]">
                  Terima kasih<br />
                  Barang yang sudah dibeli<br />
                  tidak dapat dikembalikan<br />
                </div>
                ================================
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => window.print()}
                className="flex-1 py-2 bg-[#4F46E5] hover:bg-[#6366F1] text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5"
              >
                <Printer className="w-4 h-4" />
                <span>Cetak Printer</span>
              </button>
              <button
                onClick={() => setShowStrukModal(false)}
                className="py-2 px-4 bg-[#343746] hover:bg-[#44475A] text-[#F8F8F2] rounded-xl text-xs font-bold"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [*] RUBAH QTY BARANG (Matching handlers/keranjang.py) */}
      {/* ============================================================ */}
      {showUbahQtyModal && keranjang[selectedRowIndex] && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-sm w-full border border-[#4F46E5] shadow-2xl p-5 space-y-4">
            <h3 className="font-bold text-sm text-[#F7AD31] text-center">RUBAH JUMLAH BARANG</h3>
            <div className="bg-[#1E1E2E] p-3 rounded-lg text-xs space-y-1">
              <div className="font-bold text-[#F8F8F2]">{keranjang[selectedRowIndex].nama}</div>
              <div className="flex justify-between text-[#A0A5B5]">
                <span>Harga: {formatRp(keranjang[selectedRowIndex].harga)}</span>
                <span>Qty Saat ini: {keranjang[selectedRowIndex].qty} {keranjang[selectedRowIndex].satuan}</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#A0A5B5] mb-1">QTY BARU:</label>
              <input
                type="number"
                value={tempQtyVal}
                onChange={(e) => setTempQtyVal(e.target.value)}
                className="w-full bg-[#1E1E2E] text-[#F8F8F2] font-mono text-lg font-bold p-2 rounded-lg border border-[#4F46E5] text-right"
                autoFocus
              />
            </div>

            <div className="flex gap-2 justify-end pt-2">
              <button
                onClick={() => setShowUbahQtyModal(false)}
                className="px-3 py-1.5 bg-[#343746] text-[#F8F8F2] rounded-lg text-xs"
              >
                Batal
              </button>
              <button
                onClick={() => {
                  const q = parseFloat(tempQtyVal);
                  if (!isNaN(q)) {
                    const next = [...keranjang];
                    next[selectedRowIndex].qty = q;
                    setKeranjang(next);
                  }
                  setShowUbahQtyModal(false);
                }}
                className="px-4 py-1.5 bg-[#4F46E5] text-white rounded-lg text-xs font-bold"
              >
                Simpan (ENTER)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [F9] DISKON PER ITEM DUA KOLOM (Matching handlers/aksi_lain.py) */}
      {/* ============================================================ */}
      {showDiskonItemModal && keranjang[selectedRowIndex] && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-md w-full border border-[#4F46E5] shadow-2xl p-5 space-y-4">
            <h3 className="font-bold text-sm text-[#F7AD31] text-center">DISKON PER ITEM (F9)</h3>
            <div className="bg-[#1E1E2E] p-3 rounded-lg text-xs space-y-1">
              <div className="font-bold text-[#F8F8F2]">{keranjang[selectedRowIndex].nama}</div>
              <div className="text-[#4F46E5]">Harga: {formatRp(keranjang[selectedRowIndex].harga)} · Qty: {keranjang[selectedRowIndex].qty}</div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold text-[#4F46E5] mb-1">Persen % (F4)</label>
                <input
                  type="number"
                  value={tempItemDiskonPct}
                  onChange={(e) => {
                    setTempItemDiskonPct(e.target.value);
                    setTempItemDiskonRp("0");
                  }}
                  className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2 rounded-lg border border-[#4F46E5] text-center font-bold"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#4F46E5] mb-1">Angka Rp (F5)</label>
                <input
                  type="number"
                  value={tempItemDiskonRp}
                  onChange={(e) => {
                    setTempItemDiskonRp(e.target.value);
                    setTempItemDiskonPct("0");
                  }}
                  className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2 rounded-lg border border-[#4F46E5] text-center font-bold"
                />
              </div>
            </div>

            <div className="flex gap-2 justify-end pt-2">
              <button
                onClick={() => setShowDiskonItemModal(false)}
                className="px-3 py-1.5 bg-[#343746] text-[#F8F8F2] rounded-lg text-xs"
              >
                Batal
              </button>
              <button
                onClick={() => {
                  const p = parseFloat(tempItemDiskonPct) || 0;
                  const r = parseFloat(tempItemDiskonRp) || 0;
                  const next = [...keranjang];
                  next[selectedRowIndex].diskon_pct = p;
                  next[selectedRowIndex].diskon_rp = r;
                  setKeranjang(next);
                  setShowDiskonItemModal(false);
                }}
                className="px-4 py-1.5 bg-[#4F46E5] text-white rounded-lg text-xs font-bold"
              >
                Terapkan Diskon
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [F2] VOID ITEM CONFIRMATION */}
      {/* ============================================================ */}
      {showVoidModal && keranjang[selectedRowIndex] && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-sm w-full border border-[#FF5555] shadow-2xl p-5 space-y-4 text-center">
            <h3 className="font-bold text-sm text-[#F7AD31]">HAPUS ITEM (F2 VOID)</h3>
            <p className="text-xs text-[#F8F8F2]">
              Hapus item <strong className="text-[#FF5555]">{keranjang[selectedRowIndex].nama}</strong> dari keranjang belanja?
            </p>
            <div className="flex gap-3 justify-center pt-2">
              <button
                onClick={() => {
                  setKeranjang((prev) => prev.filter((_, i) => i !== selectedRowIndex));
                  setSelectedRowIndex(0);
                  setShowVoidModal(false);
                }}
                className="px-5 py-2 bg-[#FF5555] text-white rounded-xl text-xs font-bold"
              >
                HAPUS
              </button>
              <button
                onClick={() => setShowVoidModal(false)}
                className="px-5 py-2 bg-[#343746] text-[#F8F8F2] rounded-xl text-xs font-bold"
              >
                BATAL
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [F3] OPEN PLU MANUAL */}
      {/* ============================================================ */}
      {showOpenPluModal && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-sm w-full border border-[#4F46E5] shadow-2xl p-5 space-y-3">
            <h3 className="font-bold text-sm text-[#F8F8F2]">OPEN PLU PENJUALAN MANUAL (F3)</h3>
            <div>
              <label className="block text-xs text-[#A0A5B5] mb-1">Nama Barang:</label>
              <input
                type="text"
                value={openPluNama}
                onChange={(e) => setOpenPluNama(e.target.value)}
                className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2 rounded-lg border border-[#343746] text-xs"
              />
            </div>
            <div>
              <label className="block text-xs text-[#A0A5B5] mb-1">Harga (Rp):</label>
              <input
                type="number"
                value={openPluHarga}
                onChange={(e) => setOpenPluHarga(e.target.value)}
                className="w-full bg-[#1E1E2E] text-[#50FA7B] font-bold p-2 rounded-lg border border-[#343746] text-xs"
              />
            </div>
            <div>
              <label className="block text-xs text-[#A0A5B5] mb-1">Qty:</label>
              <input
                type="number"
                value={openPluQty}
                onChange={(e) => setOpenPluQty(e.target.value)}
                className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2 rounded-lg border border-[#343746] text-xs"
              />
            </div>
            <div className="flex gap-2 justify-end pt-2">
              <button onClick={() => setShowOpenPluModal(false)} className="px-3 py-1.5 bg-[#343746] rounded text-xs text-[#F8F8F2]">Batal</button>
              <button
                onClick={() => {
                  const hrg = parseFloat(openPluHarga) || 0;
                  const q = parseFloat(openPluQty) || 1;
                  const kode = `OPN${String(keranjang.length + 1).padStart(3, '0')}`;
                  tambahItem(kode, openPluNama, hrg, q, "PC");
                  setShowOpenPluModal(false);
                }}
                className="px-4 py-1.5 bg-[#4F46E5] text-white rounded text-xs font-bold"
              >
                Simpan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [F5/F6/F7] PENDING TRANSAKSI */}
      {/* ============================================================ */}
      {showPendingModal && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-lg w-full border border-[#4F46E5] shadow-2xl p-5 space-y-4">
            <div className="flex justify-between items-center pb-2 border-b border-[#343746]">
              <h3 className="font-bold text-sm text-[#F7AD31]">
                {pendingMode === 'save' ? 'SIMPAN TRANSAKSI PENDING (F5)' : pendingMode === 'call' ? 'PILIH TRANSAKSI PENDING (F6)' : 'HAPUS TRANSAKSI PENDING (F7)'}
              </h3>
              <button onClick={() => setShowPendingModal(false)} className="text-[#A0A5B5]">✕</button>
            </div>

            {pendingMode === 'save' ? (
              <div className="space-y-3">
                <p className="text-xs text-[#A0A5B5]">Simpan sementara pesanan ini di memori kasir:</p>
                <input
                  type="text"
                  value={pendingName}
                  onChange={(e) => setPendingName(e.target.value)}
                  placeholder="Nama Pelanggan (opsional, misal: Pak Joko)"
                  className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2.5 rounded-lg border border-[#4F46E5] text-xs"
                />
                <div className="flex justify-end gap-2 pt-2">
                  <button onClick={() => setShowPendingModal(false)} className="px-3 py-1.5 bg-[#343746] rounded text-xs text-[#F8F8F2]">Batal</button>
                  <button
                    onClick={() => {
                      const item: PendingItem = {
                        id: Date.now(),
                        nama_pembeli: pendingName.trim() || `Pesanan #${pendingList.length + 1}`,
                        tanggal: new Date().toLocaleTimeString('id-ID'),
                        data: {
                          keranjang: [...keranjang],
                          diskon_global_rp: diskonGlobalRp,
                          diskon_global_persen: diskonGlobalPct,
                          biaya_tambahan: biayaTambahan
                        }
                      };
                      setPendingList([item, ...pendingList]);
                      setKeranjang([]);
                      setPendingName("");
                      setShowPendingModal(false);
                      setNotifMessage({ title: "Sukses", text: "Transaksi berhasil di-pending.", type: "success" });
                    }}
                    className="px-4 py-1.5 bg-[#4F46E5] text-white rounded text-xs font-bold"
                  >
                    Simpan Pending
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                {pendingList.length === 0 ? (
                  <p className="py-8 text-center text-[#A0A5B5] text-xs">Tidak ada data transaksi tertunda.</p>
                ) : (
                  pendingList.map((item) => (
                    <div key={item.id} className="p-3 bg-[#1E1E2E] rounded-lg border border-[#343746] flex items-center justify-between">
                      <div>
                        <div className="font-bold text-xs text-[#F8F8F2]">{item.nama_pembeli}</div>
                        <div className="text-[10px] text-[#A0A5B5]">{item.tanggal} · {item.data.keranjang.length} item</div>
                      </div>
                      <div className="flex gap-2">
                        {pendingMode === 'call' && (
                          <button
                            onClick={() => {
                              setKeranjang(item.data.keranjang);
                              setDiskonGlobalRp(item.data.diskon_global_rp);
                              setDiskonGlobalPct(item.data.diskon_global_persen);
                              setPendingList(pendingList.filter((p) => p.id !== item.id));
                              setShowPendingModal(false);
                            }}
                            className="px-3 py-1 bg-[#4F46E5] text-white rounded text-xs font-bold"
                          >
                            Panggil
                          </button>
                        )}
                        <button
                          onClick={() => {
                            setPendingList(pendingList.filter((p) => p.id !== item.id));
                          }}
                          className="px-2 py-1 bg-[#FF5555]/20 text-[#FF5555] rounded text-xs"
                        >
                          Hapus
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* MODAL: [F8] LAPORAN PENJUALAN (Matching ui/laporan.py) */}
      {/* ============================================================ */}
      {/* ============================================================ */}
      {/* MODAL: [F8] LAPORAN PENJUALAN & AUDIT (Phase B Selesai) */}
      {/* ============================================================ */}
      {showLaporanModal && (() => {
        // Filter transactions by date & batasan
        const filteredSales = salesHistory.filter((s) => {
          const matchDate = s.tgl >= laporanTglMulai && s.tgl <= laporanTglAkhir;
          if (!matchDate) return false;
          if (laporanBatasan === 'Tertentu' && laporanTertentuVal.trim()) {
            const query = laporanTertentuVal.toLowerCase();
            const matchOpr = s.operator.toLowerCase().includes(query);
            const matchKassa = s.kassa.toLowerCase().includes(query);
            const matchCara = s.caraBayar.toLowerCase().includes(query);
            return matchOpr || matchKassa || matchCara;
          }
          return true;
        }).sort((a, b) => {
          if (laporanUrutan === 'total') return b.total - a.total;
          if (laporanUrutan === 'faktur') return b.noFaktur.localeCompare(a.noFaktur);
          return (b.tgl + b.jam).localeCompare(a.tgl + a.jam);
        });

        // 1. Data Tab 1: Cara Bayar
        const mapCaraBayar: Record<string, { count: number; total: number }> = {};
        filteredSales.forEach((s) => {
          const cb = s.caraBayar || 'CASH';
          if (!mapCaraBayar[cb]) mapCaraBayar[cb] = { count: 0, total: 0 };
          mapCaraBayar[cb].count += 1;
          mapCaraBayar[cb].total += s.total;
        });

        // 2. Data Tab 2: Audit Kasir
        const mapAudit: Record<string, { faktur: number; netto: number; dskItem: number; dskGlobal: number; voidVal: number; refundVal: number }> = {};
        filteredSales.forEach((s) => {
          const opr = s.operator || 'KASIR';
          if (!mapAudit[opr]) mapAudit[opr] = { faktur: 0, netto: 0, dskItem: 0, dskGlobal: 0, voidVal: 0, refundVal: 0 };
          mapAudit[opr].faktur += 1;
          mapAudit[opr].netto += s.total;
          mapAudit[opr].dskItem += s.dskItem || 0;
          mapAudit[opr].dskGlobal += s.dskGlobal || 0;
          mapAudit[opr].voidVal += s.totalVoid || 0;
          mapAudit[opr].refundVal += s.totalRefund || 0;
        });

        // 3. Data Tab 3: Shift
        const mapShift: Record<string, { kassa: string; operator: string; shift: string; faktur: number; netto: number }> = {};
        filteredSales.forEach((s) => {
          const key = `${s.kassa}_${s.operator}_${s.shift}`;
          if (!mapShift[key]) mapShift[key] = { kassa: s.kassa, operator: s.operator, shift: s.shift, faktur: 0, netto: 0 };
          mapShift[key].faktur += 1;
          mapShift[key].netto += s.total;
        });

        // 4. Data Tab 4: Rekonsiliasi Kas
        const filteredShift = shiftHistory.filter((sh) => {
          const matchDate = sh.tanggal >= laporanTglMulai && sh.tanggal <= laporanTglAkhir;
          if (!matchDate) return false;
          if (laporanBatasan === 'Tertentu' && laporanTertentuVal.trim()) {
            return sh.operator.toLowerCase().includes(laporanTertentuVal.toLowerCase()) || sh.kassa.includes(laporanTertentuVal);
          }
          return true;
        });

        // 5. Data Tab 5: Refund
        const listRefund: any[] = [];
        filteredSales.forEach((s) => {
          s.items.forEach((itm: any) => {
            if (itm.qty < 0 || itm.isRetur) {
              listRefund.push({
                noFaktur: s.noFaktur,
                tgl: s.tgl,
                kode: itm.kode,
                nama: itm.nama,
                qty: itm.qty,
                nilai: Math.abs(itm.subtotal || (itm.qty * itm.harga))
              });
            }
          });
        });

        // 6. Data Tab 6: Laporan Barang Laku (Rekap Semua Barang Terjual)
        const mapBarangLaku: Record<string, { kode: string; nama: string; qty: number; netto: number }> = {};
        filteredSales.forEach((s) => {
          s.items.forEach((itm: any) => {
            if (itm.qty > 0) {
              if (!mapBarangLaku[itm.kode]) {
                mapBarangLaku[itm.kode] = { kode: itm.kode, nama: itm.nama, qty: 0, netto: 0 };
              }
              mapBarangLaku[itm.kode].qty += itm.qty;
              mapBarangLaku[itm.kode].netto += itm.subtotal || (itm.qty * itm.harga);
            }
          });
        });
        // SEMUA barang terjual, diurutkan berdasarkan KODE BARANG (A-Z), tanpa LIMIT
        const listBarangLaku = Object.values(mapBarangLaku).sort((a, b) => a.kode.localeCompare(b.kode));
        const totalQtyBarangLaku = listBarangLaku.reduce((sum, b) => sum + b.qty, 0);
        const totalNettoBarangLaku = listBarangLaku.reduce((sum, b) => sum + b.netto, 0);

        // Delta days
        const d1 = new Date(laporanTglMulai).getTime();
        const d2 = new Date(laporanTglAkhir).getTime();
        const deltaDays = Math.max(0, Math.round((d2 - d1) / (1000 * 60 * 60 * 24)));

        // Total Netto
        const grandTotalNetto = filteredSales.reduce((sum, s) => sum + s.total, 0);

        // Export CSV Handler
        const handleExportCSV = () => {
          let csvContent = "data:text/csv;charset=utf-8,";
          if (laporanMenu.includes("Cara Bayar")) {
            csvContent += "NO,CARA BAYAR,JUMLAH NOTA,TOTAL NETTO\n";
            Object.entries(mapCaraBayar).forEach(([cb, val], idx) => {
              csvContent += `${idx + 1},${cb},${val.count},${val.total}\n`;
            });
          } else if (laporanMenu.includes("Audit")) {
            csvContent += "NO,OPERATOR,JML FAKTUR,BRUTO,DSK ITEM,DSK GLOBAL,VOID,REFUND,NETTO\n";
            Object.entries(mapAudit).forEach(([opr, v], idx) => {
              const bruto = v.netto + v.dskItem + v.dskGlobal;
              csvContent += `${idx + 1},${opr},${v.faktur},${bruto},${v.dskItem},${v.dskGlobal},${v.voidVal},${v.refundVal},${v.netto}\n`;
            });
          } else if (laporanMenu.includes("Barang Laku")) {
            csvContent += "NO,KODE BARANG,NAMA BARANG,TOTAL QTY,TOTAL NETTO (RP)\n";
            listBarangLaku.forEach((b, idx) => {
              csvContent += `${idx + 1},${b.kode},\"${b.nama}\",${b.qty},${b.netto}\n`;
            });
          } else {
            csvContent += "NO,NO FAKTUR,TANGGAL,JAM,KASIR,CARA BAYAR,TOTAL\n";
            filteredSales.forEach((s, idx) => {
              csvContent += `${idx + 1},${s.noFaktur},${s.tgl},${s.jam},${s.operator},${s.caraBayar},${s.total}\n`;
            });
          }
          const encodedUri = encodeURI(csvContent);
          const link = document.createElement("a");
          link.setAttribute("href", encodedUri);
          link.setAttribute("download", `Laporan_${laporanMenu.replace(/[^a-zA-Z0-9]/g, '_')}_${laporanTglMulai}.csv`);
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        };

        return (
          <div className="fixed inset-0 z-50 bg-[#101018]/90 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5">
            <div className="bg-[#282A36] rounded-2xl w-full max-w-6xl border border-[#4F46E5] shadow-2xl flex flex-col max-h-[92vh] overflow-hidden">
              
              {/* 1. Header Bar */}
              <div className="bg-[#1E1E2E] border-b border-[#343746] px-5 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#4F46E5]/20 text-[#4F46E5] rounded-lg">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-[#50FA7B] flex items-center gap-2">
                      <span>📑 DASHBOARD LAPORAN & AUDIT PENJUALAN</span>
                      <span className="text-[10px] bg-[#4F46E5] text-white px-2 py-0.5 rounded font-mono">FASE B</span>
                    </h3>
                    <p className="text-[11px] text-[#A0A5B5]">
                      {namaToko} · Skema FoxPro 2.6 (hjualpos, pjualpos, kasir) · 100% Keyboard-Ready
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleExportCSV}
                    className="px-3 py-1.5 bg-[#1E1E2E] hover:bg-[#343746] text-[#50FA7B] border border-[#50FA7B]/30 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  >
                    <span>📥 Export CSV</span>
                  </button>
                  <button
                    onClick={() => window.print()}
                    className="px-3 py-1.5 bg-[#4F46E5] hover:bg-[#6366F1] text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Cetak Laporan</span>
                  </button>
                  <button
                    onClick={() => setShowLaporanModal(false)}
                    className="p-1.5 text-[#A0A5B5] hover:text-white hover:bg-[#343746] rounded-lg transition-colors ml-2"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* 2. Parameter Filter Toolbar (Persis Dialog Filter POS Lama) */}
              <div className="bg-[#242634] border-b border-[#343746] p-3 text-xs flex flex-wrap gap-4 items-center justify-between">
                <div className="flex flex-wrap items-center gap-4">
                  {/* Periode Tanggal */}
                  <div className="flex items-center gap-2 bg-[#1E1E2E] px-3 py-1.5 rounded-lg border border-[#343746]">
                    <Calendar className="w-3.5 h-3.5 text-[#4F46E5]" />
                    <span className="font-semibold text-[#A0A5B5]">Dari:</span>
                    <input
                      type="date"
                      value={laporanTglMulai}
                      onChange={(e) => setLaporanTglMulai(e.target.value)}
                      className="bg-[#282A36] text-[#F8F8F2] px-2 py-0.5 rounded border border-[#343746] text-xs font-mono"
                    />
                    <span className="font-semibold text-[#A0A5B5]">s/d:</span>
                    <input
                      type="date"
                      value={laporanTglAkhir}
                      onChange={(e) => setLaporanTglAkhir(e.target.value)}
                      className="bg-[#282A36] text-[#F8F8F2] px-2 py-0.5 rounded border border-[#343746] text-xs font-mono"
                    />
                    <span className="text-[#F7AD31] font-bold text-[11px] bg-[#F7AD31]/10 px-2 py-0.5 rounded">
                      Selama: {deltaDays} hari
                    </span>
                  </div>

                  {/* Batasan */}
                  <div className="flex items-center gap-2 bg-[#1E1E2E] px-3 py-1.5 rounded-lg border border-[#343746]">
                    <span className="text-[#A0A5B5] font-semibold">Batasan:</span>
                    <label className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="radio"
                        name="batasan"
                        checked={laporanBatasan === 'Semua'}
                        onChange={() => setLaporanBatasan('Semua')}
                        className="accent-[#4F46E5]"
                      />
                      <span>Semua</span>
                    </label>
                    <label className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="radio"
                        name="batasan"
                        checked={laporanBatasan === 'Tertentu'}
                        onChange={() => setLaporanBatasan('Tertentu')}
                        className="accent-[#4F46E5]"
                      />
                      <span>Tertentu</span>
                    </label>
                    {laporanBatasan === 'Tertentu' && (
                      <input
                        type="text"
                        placeholder="Kasir / Kassa / Opr..."
                        value={laporanTertentuVal}
                        onChange={(e) => setLaporanTertentuVal(e.target.value)}
                        className="bg-[#282A36] text-[#F8F8F2] px-2 py-0.5 rounded border border-[#4F46E5] text-xs w-28 ml-1"
                        autoFocus
                      />
                    )}
                  </div>

                  {/* Urutan */}
                  <div className="flex items-center gap-2 bg-[#1E1E2E] px-3 py-1.5 rounded-lg border border-[#343746]">
                    <span className="text-[#A0A5B5] font-semibold">Urutkan:</span>
                    <select
                      value={laporanUrutan}
                      onChange={(e: any) => setLaporanUrutan(e.target.value)}
                      className="bg-[#282A36] text-[#F8F8F2] px-2 py-0.5 rounded border border-[#343746] text-xs"
                    >
                      <option value="tgl">Tanggal & Waktu</option>
                      <option value="faktur">No Faktur</option>
                      <option value="total">Total Terbesar</option>
                    </select>
                  </div>
                </div>

                <div className="text-[11px] text-[#A0A5B5]">
                  Menampilkan <strong className="text-[#50FA7B]">{filteredSales.length}</strong> transaksi terfilter
                </div>
              </div>

              {/* 3. Main Content: Sidebar Tabs & Data Table */}
              <div className="flex-1 flex overflow-hidden">
                
                {/* Sidebar Kiri: Daftar 7 Laporan */}
                <div className="w-64 bg-[#1E1E2E] border-r border-[#343746] p-3 flex flex-col gap-1 overflow-y-auto">
                  <div className="text-[10px] uppercase font-bold text-[#A0A5B5] px-2 pb-1.5 tracking-wider">
                    Menu Laporan & Audit
                  </div>
                  {[
                    { id: "1. Kasir - Cara Bayar", desc: "Total omset per metode bayar", icon: CreditCard },
                    { id: "2. Kasir - Diskon / Refund / Void", desc: "Audit bruto, diskon & selisih", icon: DollarSign },
                    { id: "3. Kassa - Kasir - Shift", desc: "Omset per kasir & shift", icon: Clock },
                    { id: "4. Rekonsiliasi Kas (Modal/Biaya)", desc: "Modal awal, biaya & setoran", icon: CheckCircle2 },
                    { id: "5. Daftar Refund / Retur", desc: "Rincian barang diretur", icon: RotateCcw },
                    { id: "6. Laporan Barang Laku", desc: "Rekapitulasi semua barang terjual", icon: TrendingUp },
                    { id: "7. Per Nota Faktur", desc: "Rincian lengkap setiap struk", icon: Receipt },
                  ].map((tab) => {
                    const TabIcon = tab.icon;
                    const isActive = laporanMenu === tab.id;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => {
                          setLaporanMenu(tab.id);
                          setSelectedNotaDetail(null);
                        }}
                        className={`text-left p-2.5 rounded-xl transition-all flex items-start gap-2.5 ${
                          isActive
                            ? 'bg-[#4F46E5] text-white shadow-md font-bold'
                            : 'text-[#A0A5B5] hover:bg-[#282A36] hover:text-[#F8F8F2]'
                        }`}
                      >
                        <TabIcon className={`w-4 h-4 mt-0.5 shrink-0 ${isActive ? 'text-white' : 'text-[#4F46E5]'}`} />
                        <div>
                          <div className="text-xs font-semibold leading-tight">{tab.id}</div>
                          <div className={`text-[10px] leading-tight mt-0.5 ${isActive ? 'text-white/80' : 'text-[#6272A4]'}`}>
                            {tab.desc}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>

                {/* Panel Kanan: Tabel Data Laporan (Zebra Striping, Rata Kanan Angka Monospace) */}
                <div className="flex-1 bg-[#1E1E2E] p-4 flex flex-col overflow-hidden">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-bold text-sm text-[#F7AD31] flex items-center gap-2">
                      <span>{laporanMenu}</span>
                      <span className="text-[11px] font-normal text-[#A0A5B5]">
                        ({laporanTglMulai} s/d {laporanTglAkhir})
                      </span>
                    </h4>
                  </div>

                  {/* Render Table According to Tab */}
                  <div className="flex-1 overflow-auto rounded-xl border border-[#343746] bg-[#282A36]">
                    
                    {/* TAB 1: Kasir - Cara Bayar */}
                    {laporanMenu.includes("Cara Bayar") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-4 text-center w-14">NO</th>
                            <th className="py-2.5 px-4">CARA BAYAR</th>
                            <th className="py-2.5 px-4 text-right">JUMLAH NOTA</th>
                            <th className="py-2.5 px-4 text-right">TOTAL NETTO (RP)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {Object.entries(mapCaraBayar).length === 0 ? (
                            <tr><td colSpan={4} className="py-12 text-center text-[#A0A5B5]">Tidak ada data transaksi pada periode ini.</td></tr>
                          ) : (
                            Object.entries(mapCaraBayar).map(([cb, v], idx) => (
                              <tr key={cb} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                <td className="py-2.5 px-4 text-center text-[#A0A5B5]">{idx + 1}</td>
                                <td className="py-2.5 px-4 font-bold text-[#F8F8F2] flex items-center gap-2">
                                  <span className="w-2 h-2 rounded-full bg-[#50FA7B]" />
                                  <span>{cb}</span>
                                </td>
                                <td className="py-2.5 px-4 text-right text-[#A0A5B5]">{v.count} faktur</td>
                                <td className="py-2.5 px-4 text-right font-bold text-[#50FA7B]">{formatRp(v.total)}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    )}

                    {/* TAB 2: Audit Kasir (Bruto, Diskon, Void, Refund, Netto) */}
                    {laporanMenu.includes("Diskon / Refund / Void") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-3 text-center w-12">NO</th>
                            <th className="py-2.5 px-3">OPERATOR</th>
                            <th className="py-2.5 px-3 text-right">FAKTUR</th>
                            <th className="py-2.5 px-3 text-right">BRUTO (RP)</th>
                            <th className="py-2.5 px-3 text-right">DSK ITEM (RP)</th>
                            <th className="py-2.5 px-3 text-right">DSK GLOBAL (RP)</th>
                            <th className="py-2.5 px-3 text-right">VOID (RP)</th>
                            <th className="py-2.5 px-3 text-right">REFUND (RP)</th>
                            <th className="py-2.5 px-3 text-right">NETTO (RP)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {Object.entries(mapAudit).length === 0 ? (
                            <tr><td colSpan={9} className="py-12 text-center text-[#A0A5B5]">Tidak ada data penjualan pada periode ini.</td></tr>
                          ) : (
                            Object.entries(mapAudit).map(([opr, v], idx) => {
                              const bruto = v.netto + v.dskItem + v.dskGlobal;
                              return (
                                <tr key={opr} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                  <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{idx + 1}</td>
                                  <td className="py-2.5 px-3 font-bold text-[#F8F8F2]">{opr}</td>
                                  <td className="py-2.5 px-3 text-right text-[#A0A5B5]">{v.faktur}</td>
                                  <td className="py-2.5 px-3 text-right text-[#F8F8F2]">{formatRp(bruto)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#F7AD31]">{formatRp(v.dskItem)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#F7AD31]">{formatRp(v.dskGlobal)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#FF5555]">{formatRp(v.voidVal)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#FF5555]">{formatRp(v.refundVal)}</td>
                                  <td className="py-2.5 px-3 text-right font-bold text-[#50FA7B]">{formatRp(v.netto)}</td>
                                </tr>
                              );
                            })
                          )}
                        </tbody>
                      </table>
                    )}

                    {/* TAB 3: Kassa - Kasir - Shift */}
                    {laporanMenu.includes("Kassa - Kasir - Shift") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-4 text-center w-14">NO</th>
                            <th className="py-2.5 px-4 text-center">KASSA</th>
                            <th className="py-2.5 px-4">KASIR / OPERATOR</th>
                            <th className="py-2.5 px-4 text-center">SHIFT</th>
                            <th className="py-2.5 px-4 text-right">JML FAKTUR</th>
                            <th className="py-2.5 px-4 text-right">TOTAL NETTO (RP)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {Object.values(mapShift).length === 0 ? (
                            <tr><td colSpan={6} className="py-12 text-center text-[#A0A5B5]">Tidak ada data shift pada periode ini.</td></tr>
                          ) : (
                            Object.values(mapShift).map((s, idx) => (
                              <tr key={idx} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                <td className="py-2.5 px-4 text-center text-[#A0A5B5]">{idx + 1}</td>
                                <td className="py-2.5 px-4 text-center text-[#F8F8F2] font-bold">Kassa {s.kassa}</td>
                                <td className="py-2.5 px-4 text-[#F8F8F2]">{s.operator}</td>
                                <td className="py-2.5 px-4 text-center font-bold text-[#F7AD31]">Shift {s.shift}</td>
                                <td className="py-2.5 px-4 text-right text-[#A0A5B5]">{s.faktur}</td>
                                <td className="py-2.5 px-4 text-right font-bold text-[#50FA7B]">{formatRp(s.netto)}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    )}

                    {/* TAB 4: Rekonsiliasi Kas */}
                    {laporanMenu.includes("Rekonsiliasi Kas") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-3 text-center w-12">NO</th>
                            <th className="py-2.5 px-3">KASIR</th>
                            <th className="py-2.5 px-3 text-center">SHIFT</th>
                            <th className="py-2.5 px-3 text-right">MODAL AWAL</th>
                            <th className="py-2.5 px-3 text-right">BIAYA</th>
                            <th className="py-2.5 px-3 text-right">PENJUALAN</th>
                            <th className="py-2.5 px-3 text-right">UANG SISTEM</th>
                            <th className="py-2.5 px-3 text-right">SETORAN FISIK</th>
                            <th className="py-2.5 px-3 text-right">SELISIH</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {filteredShift.length === 0 ? (
                            <tr><td colSpan={9} className="py-12 text-center text-[#A0A5B5]">Tidak ada data setoran kasir fisik pada periode ini.</td></tr>
                          ) : (
                            filteredShift.map((sh, idx) => {
                              const uangSistem = sh.modal + sh.totalJual - sh.biaya;
                              const selisih = sh.setoran - uangSistem;
                              return (
                                <tr key={idx} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                  <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{idx + 1}</td>
                                  <td className="py-2.5 px-3 font-bold text-[#F8F8F2]">{sh.operator}</td>
                                  <td className="py-2.5 px-3 text-center text-[#F7AD31]">{sh.shift}</td>
                                  <td className="py-2.5 px-3 text-right text-[#A0A5B5]">{formatRp(sh.modal)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#FF5555]">{formatRp(sh.biaya)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#50FA7B]">{formatRp(sh.totalJual)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#F8F8F2] font-semibold">{formatRp(uangSistem)}</td>
                                  <td className="py-2.5 px-3 text-right text-[#F8F8F2] font-bold">{formatRp(sh.setoran)}</td>
                                  <td className={`py-2.5 px-3 text-right font-bold ${selisih < 0 ? 'text-[#FF5555]' : 'text-[#50FA7B]'}`}>
                                    {formatRp(selisih)}
                                  </td>
                                </tr>
                              );
                            })
                          )}
                        </tbody>
                      </table>
                    )}

                    {/* TAB 5: Daftar Refund / Retur */}
                    {laporanMenu.includes("Daftar Refund") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-4 text-center w-14">NO</th>
                            <th className="py-2.5 px-4">NO FAKTUR</th>
                            <th className="py-2.5 px-4 text-center">TANGGAL</th>
                            <th className="py-2.5 px-4 text-center">KODE</th>
                            <th className="py-2.5 px-4">NAMA BARANG RETUR</th>
                            <th className="py-2.5 px-4 text-center">QTY</th>
                            <th className="py-2.5 px-4 text-right">NILAI RETUR (RP)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {listRefund.length === 0 ? (
                            <tr><td colSpan={7} className="py-12 text-center text-[#A0A5B5]">Tidak ada item retur / refund pada periode ini.</td></tr>
                          ) : (
                            listRefund.map((r, idx) => (
                              <tr key={idx} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                <td className="py-2.5 px-4 text-center text-[#A0A5B5]">{idx + 1}</td>
                                <td className="py-2.5 px-4 font-bold text-[#4F46E5]">{r.noFaktur}</td>
                                <td className="py-2.5 px-4 text-center text-[#A0A5B5]">{r.tgl}</td>
                                <td className="py-2.5 px-4 text-center text-[#F7AD31]">{r.kode}</td>
                                <td className="py-2.5 px-4 text-[#F8F8F2]">{r.nama}</td>
                                <td className="py-2.5 px-4 text-center text-[#FF5555] font-bold">{r.qty}</td>
                                <td className="py-2.5 px-4 text-right text-[#FF5555] font-bold">{formatRp(r.nilai)}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    )}

                    {/* TAB 6: Laporan Barang Laku (Rekap Semua Barang Terjual) */}
                    {laporanMenu.includes("Barang Laku") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-4 text-center w-16">NO</th>
                            <th className="py-2.5 px-4 text-center w-36">KODE BARANG</th>
                            <th className="py-2.5 px-4">NAMA BARANG</th>
                            <th className="py-2.5 px-4 text-right w-36">TOTAL QTY</th>
                            <th className="py-2.5 px-4 text-right w-44">TOTAL NETTO (RP)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {listBarangLaku.length === 0 ? (
                            <tr><td colSpan={5} className="py-12 text-center text-[#A0A5B5]">Tidak ada data barang terjual pada periode ini.</td></tr>
                          ) : (
                            listBarangLaku.map((b, idx) => (
                              <tr key={b.kode} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                <td className="py-2.5 px-4 text-center text-[#A0A5B5]">{idx + 1}</td>
                                <td className="py-2.5 px-4 text-center font-bold text-[#F8F8F2]">{b.kode}</td>
                                <td className="py-2.5 px-4 font-bold text-[#F8F8F2]">{b.nama}</td>
                                <td className="py-2.5 px-4 text-right font-bold text-[#F8F8F2]">{b.qty.toLocaleString('id-ID')}</td>
                                <td className="py-2.5 px-4 text-right font-bold text-[#50FA7B]">{formatRp(b.netto)}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    )}

                    {/* TAB 7: Per Nota Faktur */}
                    {laporanMenu.includes("Per Nota") && (
                      <table className="w-full text-xs text-left">
                        <thead className="bg-[#191924] text-[#4F46E5] font-mono font-bold uppercase sticky top-0 border-b border-[#343746]">
                          <tr>
                            <th className="py-2.5 px-3 text-center w-12">NO</th>
                            <th className="py-2.5 px-3">NO FAKTUR</th>
                            <th className="py-2.5 px-3 text-center">TANGGAL</th>
                            <th className="py-2.5 px-3 text-center">JAM</th>
                            <th className="py-2.5 px-3">KASIR</th>
                            <th className="py-2.5 px-3 text-center">CARA BAYAR</th>
                            <th className="py-2.5 px-3 text-right">TOTAL FAKTUR (RP)</th>
                            <th className="py-2.5 px-3 text-center">RINCIAN</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#343746]/40 font-mono">
                          {filteredSales.length === 0 ? (
                            <tr><td colSpan={8} className="py-12 text-center text-[#A0A5B5]">Tidak ada faktur pada periode ini.</td></tr>
                          ) : (
                            filteredSales.map((s, idx) => (
                              <tr key={s.noFaktur} className={idx % 2 === 0 ? 'bg-[#282A36]' : 'bg-[#222430]'}>
                                <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{idx + 1}</td>
                                <td className="py-2.5 px-3 font-bold text-[#4F46E5]">{s.noFaktur}</td>
                                <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{s.tgl}</td>
                                <td className="py-2.5 px-3 text-center text-[#A0A5B5]">{s.jam}</td>
                                <td className="py-2.5 px-3 text-[#F8F8F2]">{s.operator}</td>
                                <td className="py-2.5 px-3 text-center font-bold text-[#F7AD31]">{s.caraBayar}</td>
                                <td className="py-2.5 px-3 text-right font-bold text-[#50FA7B]">{formatRp(s.total)}</td>
                                <td className="py-2.5 px-3 text-center">
                                  <button
                                    onClick={() => setSelectedNotaDetail(s)}
                                    className="px-2 py-1 bg-[#4F46E5]/20 hover:bg-[#4F46E5] text-[#4F46E5] hover:text-white rounded text-[11px] font-sans font-semibold transition-colors"
                                  >
                                    Lihat Item
                                  </button>
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    )}

                  </div>

                  {/* Detail Faktur Modal Sub-overlay */}
                  {selectedNotaDetail && (
                    <div className="fixed inset-0 z-60 bg-black/70 flex items-center justify-center p-4">
                      <div className="bg-[#282A36] rounded-xl max-w-lg w-full border border-[#4F46E5] shadow-2xl p-4 space-y-3">
                        <div className="flex justify-between items-center pb-2 border-b border-[#343746]">
                          <div>
                            <div className="font-bold text-sm text-[#50FA7B]">FAKTUR: {selectedNotaDetail.noFaktur}</div>
                            <div className="text-[11px] text-[#A0A5B5]">
                              {selectedNotaDetail.tgl} {selectedNotaDetail.jam} · Kasir: {selectedNotaDetail.operator} · {selectedNotaDetail.caraBayar}
                            </div>
                          </div>
                          <button onClick={() => setSelectedNotaDetail(null)} className="text-[#A0A5B5] hover:text-white">✕</button>
                        </div>

                        <div className="max-h-60 overflow-y-auto space-y-1.5 font-mono text-xs">
                          {selectedNotaDetail.items.map((it: any, i: number) => (
                            <div key={i} className="flex justify-between p-2 bg-[#1E1E2E] rounded border border-[#343746]/50">
                              <div>
                                <div className="text-[#F8F8F2] font-sans font-bold">{it.nama}</div>
                                <div className="text-[10px] text-[#A0A5B5]">
                                  {it.qty} {it.satuan} × {formatRp(it.harga)}
                                </div>
                              </div>
                              <div className="text-right font-bold text-[#50FA7B]">
                                {formatRp(it.subtotal)}
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="pt-2 border-t border-[#343746] flex justify-between items-center text-xs">
                          <span className="font-bold text-[#F8F8F2]">TOTAL AKHIR:</span>
                          <span className="font-bold text-base text-[#50FA7B] font-mono">{formatRp(selectedNotaDetail.total)}</span>
                        </div>

                        <button
                          onClick={() => setSelectedNotaDetail(null)}
                          className="w-full py-2 bg-[#343746] hover:bg-[#44475A] text-[#F8F8F2] rounded-lg text-xs font-bold font-sans"
                        >
                          Tutup Rincian
                        </button>
                      </div>
                    </div>
                  )}

                  {/* 4. Footer Bar */}
                  <div className="mt-3 bg-[#191924] p-3 rounded-xl border border-[#343746] flex items-center justify-between">
                    <div className="text-xs text-[#A0A5B5] flex items-center gap-3">
                      <span>Total Data: <strong className="text-[#F8F8F2]">
                        {laporanMenu.includes("Barang Laku") ? `${listBarangLaku.length} baris` : `${filteredSales.length} faktur`}
                      </strong></span>
                      <span>·</span>
                      <span className="text-[#6272A4] font-mono">[F8] Laporan · [ESC] Kembali ke POS</span>
                    </div>

                    <div className="flex items-center gap-4">
                      {laporanMenu.includes("Barang Laku") ? (
                        <>
                          <div className="text-xs text-[#A0A5B5]">
                            Total Qty: <strong className="text-[#F8F8F2] font-mono text-sm">{totalQtyBarangLaku.toLocaleString('id-ID')}</strong>
                          </div>
                          <span className="text-[#343746]">|</span>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-[#A0A5B5] uppercase">Total Netto:</span>
                            <span className="text-base font-bold font-mono text-[#50FA7B]">
                              {formatRp(totalNettoBarangLaku)}
                            </span>
                          </div>
                        </>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-[#A0A5B5] uppercase">Total Netto:</span>
                          <span className="text-base font-bold font-mono text-[#50FA7B]">
                            {formatRp(grandTotalNetto)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              </div>

            </div>
          </div>
        );
      })()}

      {/* ============================================================ */}
      {/* MODAL: LOGIN KASIR (Matching ui/login.py) */}
      {/* ============================================================ */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-sm w-full border border-[#4F46E5] shadow-2xl p-6 space-y-4 text-center">
            <h3 className="font-bold text-base text-[#4F46E5]">◉ LOGIN KASIR</h3>
            <p className="text-xs text-[#A0A5B5]">{namaToko} · POS V3</p>

            <div className="space-y-3 text-left">
              <div>
                <label className="block text-xs font-semibold text-[#A0A5B5] mb-1">USER ID:</label>
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2.5 rounded-lg border border-[#343746] text-xs font-bold"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#A0A5B5] mb-1">PASSWORD:</label>
                <input
                  type="password"
                  defaultValue="1"
                  className="w-full bg-[#1E1E2E] text-[#F8F8F2] p-2.5 rounded-lg border border-[#343746] text-xs font-bold"
                />
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowLoginModal(false)}
                className="flex-1 py-2 bg-[#343746] text-[#F8F8F2] rounded-xl text-xs"
              >
                Batal
              </button>
              <button
                onClick={() => {
                  setNamaUser(userId === '1' ? 'Administrator' : `Kasir-${userId}`);
                  setShowLoginModal(false);
                  setNotifMessage({ title: "Sukses", text: `Selamat datang, ${userId === '1' ? 'Administrator' : `Kasir-${userId}`}!`, type: "success" });
                }}
                className="flex-1 py-2 bg-[#4F46E5] text-white rounded-xl text-xs font-bold"
              >
                LOGIN
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* NOTIFIKASI POPUP (Matching ui/dialogs.py info_kk) */}
      {/* ============================================================ */}
      {notifMessage && (
        <div className="fixed inset-0 z-50 bg-[#101018]/80 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-[#282A36] rounded-2xl max-w-sm w-full border border-[#4F46E5] shadow-2xl p-6 text-center space-y-3">
            <div className="text-3xl">
              {notifMessage.type === 'error' ? '✕' : notifMessage.type === 'success' ? '✓' : 'ℹ'}
            </div>
            <h4 className="font-bold text-sm text-[#F7AD31] uppercase">{notifMessage.title}</h4>
            <p className="text-xs text-[#F8F8F2] whitespace-pre-line leading-relaxed">{notifMessage.text}</p>
            <button
              onClick={() => setNotifMessage(null)}
              className="mt-3 px-6 py-2 bg-[#343746] hover:bg-[#44475A] text-[#4F46E5] font-bold rounded-xl text-xs"
              autoFocus
            >
              OK (ENTER / ESC)
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
