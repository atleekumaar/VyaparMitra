import React, { useEffect, useState } from 'react';
import { Search, Filter, Package, ArrowUpRight, Sparkles, X } from 'lucide-react';
import { api } from '../api/client';
import { ProductDetail, ProductListItem } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';
import { useLanguage } from '../i18n/LanguageContext';

export const ProductsPage: React.FC = () => {
  const { t, language } = useLanguage();
  const [products, setProducts] = useState<ProductListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedProduct, setSelectedProduct] = useState<ProductDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getProducts({
        search: searchTerm || undefined,
        category: selectedCategory || undefined,
        limit: 100,
      });
      setProducts(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load product catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadProducts();
  };

  const handleOpenDetail = async (productId: string) => {
    setLoadingDetail(true);
    try {
      const detail = await api.getProductDetail(productId);
      setSelectedProduct(detail);
    } catch (err: any) {
      alert(`Could not load details for ${productId}: ${err?.message}`);
    } finally {
      setLoadingDetail(false);
    }
  };

  const categories = Array.from(new Set(products.map((p) => p.category))).filter(Boolean);

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl lg:text-2xl font-black text-[#002970] dark:text-white">
            {t('products_title', 'Product Catalog & Demand Intelligence')}
          </h2>
          <p className="text-xs text-[#4F6A94] dark:text-blue-200 mt-0.5 font-medium">
            {t('products_subtitle', 'Monitor SKU margins, historical revenues, and 7-day predicted demand units.')}
          </p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#E8F4FD] dark:bg-[#132342] text-[#002970] dark:text-[#00BAF2] border border-[#CDE5F7] dark:border-[#1E3A6E] self-start sm:self-auto shadow-2xs">
          {t('total_catalog', 'Total Catalog:')} {products.length} SKUs
        </span>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-paytm transition-colors">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-[#4F6A94] absolute left-3 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('search_products_placeholder', 'Search by product name or SKU ID...')}
            className="w-full pl-9 pr-3 py-2.5 text-xs rounded-xl border border-[#CDE5F7] dark:border-[#1E3A6E] bg-[#F0F8FE] dark:bg-[#0B1528] text-[#002970] dark:text-white focus:bg-white dark:focus:bg-[#132342] focus:outline-none focus:ring-2 focus:ring-[#00BAF2] font-semibold"
          />
        </form>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-[#00BAF2]" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3.5 py-2 text-xs rounded-xl border border-[#CDE5F7] dark:border-[#1E3A6E] bg-white dark:bg-[#0B1528] text-[#002970] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#00BAF2] font-semibold shadow-2xs"
          >
            <option value="">{t('all_categories', 'All Categories')}</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <Button variant="primary" size="sm" onClick={loadProducts} className="font-bold shadow-xs">
            {t('apply_filter', 'Apply')}
          </Button>
        </div>
      </div>

      {/* Product Table */}
      {loading ? (
        <TableSkeleton rows={8} />
      ) : error ? (
        <ErrorBanner message={error} onRetry={loadProducts} />
      ) : products.length === 0 ? (
        <EmptyState
          title={language === 'hindi' ? 'कोई सामग्री नहीं मिली' : 'No Products Found'}
          message={language === 'hindi' ? 'दिए गए फ़िल्टर के अनुसार कोई उत्पाद उपलब्ध नहीं है।' : 'No products match your current search or category filter.'}
          actionText={language === 'hindi' ? 'फ़िल्टर हटाएं' : 'Clear Filters'}
          onAction={() => {
            setSearchTerm('');
            setSelectedCategory('');
          }}
        />
      ) : (
        <div className="bg-white dark:bg-[#0F1D38] rounded-2xl border-2 border-[#CDE5F7] dark:border-[#1E3A6E] overflow-hidden shadow-paytm transition-colors">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F0F8FE] dark:bg-[#0B1528] border-b border-[#CDE5F7] dark:border-[#1E3A6E] text-[#002970] dark:text-blue-100 font-extrabold uppercase tracking-wide">
                <tr>
                  <th className="py-3 px-4">{t('col_product', 'SKU / Product')}</th>
                  <th className="py-3 px-4">{t('col_category', 'Category')}</th>
                  <th className="py-3 px-4">{t('col_unit_price', 'Price')}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'कुल बिक्री' : 'Revenue'}</th>
                  <th className="py-3 px-4">{language === 'hindi' ? 'बिकी यूनिट्स' : 'Units Sold'}</th>
                  <th className="py-3 px-4">{t('col_forecast_7d', '7D Demand')}</th>
                  <th className="py-3 px-4">{t('col_stock_status', 'Status')}</th>
                  <th className="py-3 px-4 text-right">{t('col_action', 'Action')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E8F4FD] dark:divide-[#172E58]">
                {products.map((p) => (
                  <tr key={p.product_id} className="hover:bg-[#F0F8FE] dark:hover:bg-[#132342] transition-colors">
                    <td className="py-3 px-4 font-bold text-[#002970] dark:text-white">
                      <div>{p.product_name}</div>
                      <div className="text-[10px] text-[#4F6A94] dark:text-blue-200 font-mono font-semibold">{p.product_id}</div>
                    </td>
                    <td className="py-3 px-4 text-[#4F6A94] dark:text-blue-200 font-medium">{p.category}</td>
                    <td className="py-3 px-4 font-extrabold text-[#002970] dark:text-white">₹{p.selling_price.toFixed(2)}</td>
                    <td className="py-3 px-4 font-extrabold text-[#008A54] dark:text-[#00E68A]">₹{p.total_revenue.toLocaleString()}</td>
                    <td className="py-3 px-4 font-bold text-[#002970] dark:text-white">{p.total_units}</td>
                    <td className="py-3 px-4">
                      <span className="font-extrabold text-[#00BAF2]">
                        {p.forecast_7d_units > 0 ? `${p.forecast_7d_units} units` : '—'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <Badge
                        variant={
                          p.status === 'STAR'
                            ? 'success'
                            : p.status === 'FOCUS'
                            ? 'high'
                            : 'neutral'
                        }
                      >
                        {p.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenDetail(p.product_id)}
                        className="text-xs py-1 px-3 dark:bg-[#132342] dark:border-[#1E3A6E] dark:text-white font-bold"
                      >
                        {language === 'hindi' ? 'विवरण' : 'Deep View'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Product Detail Modal */}
      <Modal
        isOpen={!!selectedProduct}
        onClose={() => setSelectedProduct(null)}
        title={selectedProduct?.product_name || 'Product Details'}
        subtitle={selectedProduct ? `SKU: ${selectedProduct.product_id} • ${selectedProduct.category}` : undefined}
      >
        {selectedProduct && (
          <div className="space-y-4 text-xs text-[#002970] dark:text-white">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E]">
                <span className="text-[#4F6A94] dark:text-blue-200 block text-[10px] font-bold uppercase">Selling Price</span>
                <span className="text-base font-black text-[#002970] dark:text-white mt-1 block">₹{selectedProduct.selling_price.toFixed(2)}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E]">
                <span className="text-[#4F6A94] dark:text-blue-200 block text-[10px] font-bold uppercase">Total Revenue</span>
                <span className="text-base font-black text-[#008A54] dark:text-[#00E68A] mt-1 block">₹{selectedProduct.total_revenue.toLocaleString()}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E]">
                <span className="text-[#4F6A94] dark:text-blue-200 block text-[10px] font-bold uppercase">Units Sold</span>
                <span className="text-base font-black text-[#002970] dark:text-white mt-1 block">{selectedProduct.total_units}</span>
              </div>
              <div className="p-3 rounded-xl bg-[#F0F8FE] dark:bg-[#132342] border border-[#CDE5F7] dark:border-[#1E3A6E]">
                <span className="text-[#4F6A94] dark:text-blue-200 block text-[10px] font-bold uppercase">7D Forecast</span>
                <span className="text-base font-black text-[#00BAF2] mt-1 block">{selectedProduct.forecast_7d_units} units</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#E8F8F0] dark:bg-[#00B970]/15 border border-[#B6E8D0] dark:border-[#00B970]/30 space-y-1">
              <span className="font-bold text-[#008A54] dark:text-[#00E68A] block">Stock Health:</span>
              <p className="text-xs text-[#008A54] dark:text-blue-100 font-medium">
                {selectedProduct.stock_status_text || 'Current inventory is stable based on trailing 14-day velocity.'}
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="navy" onClick={() => setSelectedProduct(null)}>
                {language === 'hindi' ? 'बंद करें' : 'Close'}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
