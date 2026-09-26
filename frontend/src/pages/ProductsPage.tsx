import React, { useEffect, useState } from 'react';
import { Search, Filter, Package, ArrowUpRight, Sparkles, X } from 'lucide-react';
import { api } from '../api/client';
import { ProductDetail, ProductListItem } from '../types';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { TableSkeleton } from '../components/LoadingSkeleton';
import { ErrorBanner, EmptyState } from '../components/EmptyState';

export const ProductsPage: React.FC = () => {
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
          <h2 className="text-xl font-bold text-paytm-dark">Product Catalog & Demand Intelligence</h2>
          <p className="text-xs text-paytm-muted mt-0.5">
            Monitor SKU margins, historical revenues, and 7-day predicted demand units.
          </p>
        </div>
        <Badge variant="info">Total Catalog: {products.length} SKUs</Badge>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-paytm-border p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xs">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search product ID or title..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-paytm-border bg-slate-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-paytm-blue"
          />
        </form>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-paytm-border bg-white text-paytm-text focus:outline-none focus:ring-2 focus:ring-paytm-blue"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <Button variant="secondary" size="sm" onClick={loadProducts}>
            Apply
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
          title="No Products Found"
          message="No products match your current search or category filter."
          actionText="Clear Filters"
          onAction={() => {
            setSearchTerm('');
            setSelectedCategory('');
          }}
        />
      ) : (
        <div className="bg-white rounded-xl border border-paytm-border overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-paytm-border text-paytm-muted font-semibold">
                <tr>
                  <th className="py-3 px-4">SKU / Product</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Price</th>
                  <th className="py-3 px-4">Revenue</th>
                  <th className="py-3 px-4">Units Sold</th>
                  <th className="py-3 px-4">7D Demand Forecast</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {products.map((p) => (
                  <tr key={p.product_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-semibold text-paytm-dark">
                      <div>{p.product_name}</div>
                      <div className="text-[10px] text-paytm-muted font-mono">{p.product_id}</div>
                    </td>
                    <td className="py-3 px-4 text-paytm-muted">{p.category}</td>
                    <td className="py-3 px-4 font-medium">₹{p.selling_price.toFixed(2)}</td>
                    <td className="py-3 px-4 font-semibold text-emerald-700">₹{p.total_revenue.toLocaleString()}</td>
                    <td className="py-3 px-4">{p.total_units}</td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-paytm-blue">
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
                      >
                        Deep View
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
      {selectedProduct && (
        <Modal
          isOpen={true}
          onClose={() => setSelectedProduct(null)}
          title={selectedProduct.product_name}
          subtitle={`SKU: ${selectedProduct.product_id} • Category: ${selectedProduct.category}`}
          footer={
            <Button variant="secondary" size="sm" onClick={() => setSelectedProduct(null)}>
              Close
            </Button>
          }
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">Selling Price</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">₹{selectedProduct.selling_price.toFixed(2)}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-[10px] uppercase font-bold text-paytm-muted">Unit Cost</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">₹{selectedProduct.unit_cost.toFixed(2)}</p>
            </div>
            <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
              <span className="text-[10px] uppercase font-bold text-emerald-800">Gross Margin</span>
              <p className="text-base font-bold text-emerald-700 mt-0.5">₹{selectedProduct.margin.toFixed(2)}</p>
            </div>
            <div className="p-3 bg-paytm-light rounded-lg border border-paytm-border">
              <span className="text-[10px] uppercase font-bold text-paytm-blue">7D Demand Forecast</span>
              <p className="text-base font-bold text-paytm-dark mt-0.5">{selectedProduct.forecast_7d_units} units</p>
            </div>
          </div>

          {/* Cross-Sell Associations */}
          <div className="mt-4 pt-4 border-t border-slate-100">
            <div className="flex items-center gap-1.5 text-xs font-bold text-paytm-dark mb-2">
              <Sparkles className="w-3.5 h-3.5 text-paytm-blue" />
              <span>Cross-Sell Affinities (Phase 4 Association Rules)</span>
            </div>
            {selectedProduct.cross_sell_recommendations.length === 0 ? (
              <p className="text-xs text-paytm-muted">No cross-sell association pairs flagged above confidence threshold.</p>
            ) : (
              <div className="space-y-2">
                {selectedProduct.cross_sell_recommendations.map((cs, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                    <div>
                      <span className="font-semibold text-paytm-dark">{cs.paired_sku}</span>
                      <span className="text-paytm-muted ml-2">({(cs.confidence * 100).toFixed(0)}% co-purchase affinity)</span>
                    </div>
                    <Badge variant="info">{cs.action}</Badge>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Decisions */}
          {selectedProduct.active_recommendations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-slate-100">
              <h4 className="text-xs font-bold text-paytm-dark mb-2">Active Recommendations on this SKU</h4>
              <div className="space-y-2">
                {selectedProduct.active_recommendations.map((ar) => (
                  <div key={ar.recommendation_id} className="p-2.5 rounded-lg border border-paytm-border bg-paytm-light/40 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-paytm-dark">{ar.title}</span>
                      <Badge variant={ar.priority_band === 'CRITICAL' ? 'critical' : 'high'}>{ar.priority_band}</Badge>
                    </div>
                    <p className="text-paytm-muted mt-1">{ar.action}</p>
                    <p className="text-[11px] text-emerald-700 font-semibold mt-1">Impact: ₹{ar.expected_impact.toLocaleString()}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  );
};
