/**
 * TCM Learning Assistant - Frontend Application
 * 中医学习助手前端应用
 */

// API 基础路径
const API_BASE = '';

// 状态管理
const state = {
    symptoms: [],
    formulas: [],
    herbs: [],
    categories: [],
    currentCategory: null
};

// ============================================
// 页面导航
// ============================================

function showPage(pageName) {
    // 更新导航按钮状态
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === pageName);
    });
    
    // 切换页面显示
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`page-${pageName}`).classList.add('active');
    
    // 加载数据
    if (pageName === 'formulas' && state.formulas.length === 0) {
        loadFormulas();
        loadCategories();
    } else if (pageName === 'herbs' && state.herbs.length === 0) {
        loadHerbs();
    }
}

// ============================================
// 方剂相关
// ============================================

async function loadFormulas() {
    const loading = document.getElementById('formula-loading');
    const list = document.getElementById('formula-list');
    
    loading.style.display = 'flex';
    list.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/formulas/`);
        const data = await response.json();
        state.formulas = data;
        renderFormulas(data);
    } catch (error) {
        showToast('加载方剂失败');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/formulas/categories/list`);
        const categories = await response.json();
        state.categories = categories;
        renderCategories(categories);
    } catch (error) {
        console.error('加载分类失败', error);
    }
}

function renderCategories(categories) {
    const container = document.getElementById('category-filter');
    container.innerHTML = `
        <button class="category-chip active" onclick="filterByCategory(null)">全部</button>
        ${categories.map(cat => `
            <button class="category-chip" onclick="filterByCategory('${cat}')">${cat}</button>
        `).join('')}
    `;
}

function filterByCategory(category) {
    state.currentCategory = category;
    
    // 更新选中状态
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.classList.toggle('active', chip.textContent.trim() === (category || '全部'));
    });
    
    // 筛选显示
    if (category) {
        const filtered = state.formulas.filter(f => f.category && f.category.includes(category));
        renderFormulas(filtered);
    } else {
        renderFormulas(state.formulas);
    }
}

function renderFormulas(formulas) {
    const container = document.getElementById('formula-list');
    
    if (formulas.length === 0) {
        container.innerHTML = '<div class="empty-state" style="text-align: center; padding: 48px; color: var(--text-secondary);">暂无数据</div>';
        return;
    }
    
    container.innerHTML = formulas.map(formula => `
        <div class="formula-card" onclick="showFormulaDetail('${formula.id}')">
            <div class="formula-name">${formula.name}</div>
            ${formula.category ? `<div class="formula-category">${formula.category}</div>` : ''}
            <div class="formula-efficacy">${formula.efficacy || ''}</div>
            <div class="formula-source">${formula.source || ''}</div>
        </div>
    `).join('');
}

async function searchFormulas() {
    const keyword = document.getElementById('formula-search').value.trim();
    if (!keyword) {
        renderFormulas(state.formulas);
        return;
    }
    
    const loading = document.getElementById('formula-loading');
    loading.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_BASE}/formulas/search?keyword=${encodeURIComponent(keyword)}&limit=50`);
        const data = await response.json();
        renderFormulas(data.map(r => r.formula));
    } catch (error) {
        showToast('搜索失败');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}

async function showFormulaDetail(formulaId) {
    const modal = document.getElementById('formula-modal');
    const detail = document.getElementById('formula-detail');
    
    modal.classList.add('active');
    detail.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const [formulaRes, variationsRes] = await Promise.all([
            fetch(`${API_BASE}/formulas/${formulaId}`),
            fetch(`${API_BASE}/formulas/${formulaId}/variations`)
        ]);
        
        const formula = await formulaRes.json();
        const variations = await variationsRes.json();
        
        detail.innerHTML = `
            <div class="formula-detail">
                <div class="detail-header">
                    <div class="detail-name">${formula.name}</div>
                    <div class="detail-meta">
                        ${formula.category ? `<span class="meta-tag">${formula.category}</span>` : ''}
                    </div>
                </div>
                
                ${formula.classic_text ? `
                <div class="detail-section classic-text-section">
                    <div class="classic-text">"${formula.classic_text}"</div>
                    <div class="classic-source">—— ${formula.classic_source}</div>
                </div>
                ` : ''}
                
                <div class="detail-section">
                    <h4>组成</h4>
                    <div class="composition-list">
                        ${formula.composition ? formula.composition.map(comp => `
                            <div class="composition-item" onclick="showHerbDetailByName('${comp.herb}')">
                                <span class="herb-name">${comp.herb}</span>${comp.note ? `<span class="herb-note">（${comp.note}）</span>` : ''}
                                ${comp.dosage ? `<span class="dosage">${comp.dosage}</span>` : ''}
                                ${comp.role ? `<span class="role">${comp.role}</span>` : ''}
                            </div>
                        `).join('') : '暂无'}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>功效</h4>
                    <div class="detail-text">${formula.efficacy || '暂无'}</div>
                </div>
                
                <div class="detail-section">
                    <h4>主治</h4>
                    <div class="detail-text">${formula.indications || '暂无'}</div>
                </div>
                
                ${formula.classic_usage ? `
                <div class="detail-section">
                    <h4>煎服法 <span class="section-source">原文</span></h4>
                    <div class="detail-text classic-usage">${formula.classic_usage}</div>
                </div>
                ` : ''}
                
                ${formula.usage && !formula.classic_usage ? `
                <div class="detail-section">
                    <h4>用法</h4>
                    <div class="detail-text">${formula.usage}</div>
                </div>
                ` : ''}
                
                ${formula.caution ? `
                <div class="detail-section">
                    <h4>禁忌</h4>
                    <div class="detail-text" style="color: #e57373;">${formula.caution}</div>
                </div>
                ` : ''}
                
                ${(variations.inherited_from?.length > 0 || (variations.derived_to && variations.derived_to.length > 0)) ? `
                <div class="detail-section">
                    <h4>方剂变化</h4>
                    <div class="variations-section">
                        ${variations.inherited_from && variations.inherited_from.length > 0 ? variations.inherited_from.map(v => `
                            <div class="variation-item">
                                <div class="variation-name">由「${v.name}」加减而来</div>
                                <div class="variation-changes">${formatVariations(v.variations)}</div>
                                ${v.indication_change ? `<div class="variation-indication">主治：${v.indication_change}</div>` : ''}
                            </div>
                        `).join('') : ''}
                        ${variations.derived_to && variations.derived_to.length > 0 ? variations.derived_to.map(v => `
                            <div class="variation-item">
                                <div class="variation-name">${v.name}</div>
                                <div class="variation-changes">${formatVariations(v.variations)}</div>
                                ${v.indication_change ? `<div class="variation-indication">主治：${v.indication_change}</div>` : ''}
                            </div>
                        `).join('') : ''}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    } catch (error) {
        detail.innerHTML = '<div style="padding: 32px; text-align: center; color: var(--text-secondary);">加载失败</div>';
        console.error(error);
    }
}

function formatVariations(variations) {
    if (!variations || variations.length === 0) return '';
    
    const parts = [];
    variations.forEach(v => {
        const dosage = v.new_dosage || v.original_dosage || '';
        const actionMap = {
            'add': '加',
            'remove': '减',
            'modify': '改'
        };
        const action = actionMap[v.action] || v.action;
        
        if (v.action === 'modify') {
            parts.push(`${action}: ${v.herb} ${v.original_dosage || ''}→${v.new_dosage || ''}`);
        } else {
            parts.push(`${action}: ${v.herb}${dosage ? ' ' + dosage : ''}`);
        }
    });
    
    return parts.join('；');
}

function closeModal() {
    document.getElementById('formula-modal').classList.remove('active');
}

// ============================================
// 药材相关
// ============================================

async function loadHerbs() {
    const loading = document.getElementById('herb-loading');
    const list = document.getElementById('herb-list');
    
    loading.style.display = 'flex';
    list.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/herbs/?limit=500`);
        const data = await response.json();
        state.herbs = data.herbs || data;
        renderHerbs(state.herbs);
    } catch (error) {
        showToast('加载药材失败');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}

function renderHerbs(herbs) {
    const container = document.getElementById('herb-list');
    
    // 过滤无效数据
    const validHerbs = herbs.filter(herb => herb && herb.id && herb.name);
    
    if (!validHerbs || validHerbs.length === 0) {
        container.innerHTML = '<div class="empty-state" style="text-align: center; padding: 48px; color: var(--text-secondary);">暂无数据</div>';
        return;
    }
    
    container.innerHTML = validHerbs.map(herb => `
        <div class="herb-card" onclick="showHerbDetail('${herb.id}')">
            <div class="herb-name">${herb.name}</div>
            ${herb.grade ? `<div class="herb-grade ${getGradeClass(herb.grade)}">${herb.grade}</div>` : ''}
            <div class="herb-nature">${herb.nature || ''} ${herb.flavor ? (Array.isArray(herb.flavor) ? herb.flavor.join('、') : herb.flavor) : ''}</div>
        </div>
    `).join('');
}

function getGradeClass(grade) {
    const map = {
        '上品': 'upper',
        '中品': 'middle',
        '下品': 'lower'
    };
    return map[grade] || 'other';
}

async function searchHerbs() {
    const keyword = document.getElementById('herb-search').value.trim();
    if (!keyword) {
        renderHerbs(state.herbs);
        return;
    }
    
    const loading = document.getElementById('herb-loading');
    loading.style.display = 'flex';
    
    try {
        const response = await fetch(`${API_BASE}/herbs/search?keyword=${encodeURIComponent(keyword)}&limit=50`);
        const data = await response.json();
        // 搜索结果格式: [{herb: {...}, score: ..., matched_fields: [...]}]
        // 需要提取 herb 字段并过滤无效值
        const herbs = Array.isArray(data) 
            ? data.map(item => item.herb).filter(h => h && h.id) 
            : (data.herbs || []);
        console.log('搜索结果:', herbs.length, '条');
        renderHerbs(herbs);
    } catch (error) {
        showToast('搜索失败');
        console.error(error);
    } finally {
        loading.style.display = 'none';
    }
}

async function showHerbDetail(herbId) {
    const modal = document.getElementById('herb-modal');
    const detail = document.getElementById('herb-detail');
    
    modal.classList.add('active');
    detail.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        const response = await fetch(`${API_BASE}/herbs/${herbId}`);
        const herb = await response.json();
        
        detail.innerHTML = `
            <div class="herb-detail">
                <div class="herb-detail-header">
                    <div>
                        <div class="herb-detail-name">${herb.name}</div>
                        ${herb.grade ? `<div class="herb-detail-grade ${getGradeClass(herb.grade)}">${herb.grade}</div>` : ''}
                    </div>
                </div>
                
                <div class="nature-tags">
                    ${herb.nature ? `<span class="nature-tag">${herb.nature}</span>` : ''}
                    ${herb.flavor ? `<span class="nature-tag">${Array.isArray(herb.flavor) ? herb.flavor.join('、') : herb.flavor}</span>` : ''}
                    ${herb.meridian ? `<span class="nature-tag">归${Array.isArray(herb.meridian) ? herb.meridian.join('、') : herb.meridian}经</span>` : ''}
                </div>
                
                ${herb.efficacy ? `
                <div class="detail-section">
                    <h4>功效</h4>
                    <div class="detail-text">${herb.efficacy}</div>
                </div>
                ` : ''}
                
                ${herb.indications ? `
                <div class="detail-section">
                    <h4>主治</h4>
                    <div class="detail-text">${herb.indications}</div>
                </div>
                ` : ''}
                
                ${herb.classic_text ? `
                <div class="detail-section">
                    <h4>经典原文</h4>
                    <div class="classic-text">${herb.classic_text}</div>
                </div>
                ` : ''}
                
                ${herb.dosage ? `
                <div class="detail-section">
                    <h4>用量</h4>
                    <div class="detail-text">${herb.dosage}</div>
                </div>
                ` : ''}
                
                ${herb.contraindications ? `
                <div class="detail-section">
                    <h4>禁忌</h4>
                    <div class="detail-text" style="color: #e57373;">${herb.contraindications}</div>
                </div>
                ` : ''}
            </div>
        `;
    } catch (error) {
        detail.innerHTML = '<div style="padding: 32px; text-align: center; color: var(--text-secondary);">加载失败</div>';
        console.error(error);
    }
}

function closeHerbModal() {
    document.getElementById('herb-modal').classList.remove('active');
}

async function showHerbDetailByName(herbName) {
    const modal = document.getElementById('herb-modal');
    const detail = document.getElementById('herb-detail');
    
    modal.classList.add('active');
    detail.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    try {
        // 先用搜索 API 检查药材是否存在（避免 404 报错）
        const searchResponse = await fetch(`${API_BASE}/herbs/search?keyword=${encodeURIComponent(herbName)}&limit=1`);
        const searchData = await searchResponse.json();
        
        // 检查搜索结果是否匹配
        const found = Array.isArray(searchData) && searchData.length > 0 && searchData[0].herb.name === herbName;
        
        if (!found) {
            detail.innerHTML = `
                <div class="herb-detail">
                    <div class="herb-detail-header">
                        <div class="herb-detail-name">${herbName}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-text" style="color: var(--text-secondary); text-align: center; padding: 24px;">
                            该药材暂无详细信息<br>
                            <span style="font-size: 0.85rem;">药材库持续完善中，敬请期待</span>
                        </div>
                    </div>
                </div>
            `;
            return;
        }
        
        // 药材存在，获取详情
        const herb = searchData[0].herb;
        
        // 复用 showHerbDetail 的渲染逻辑
        detail.innerHTML = `
            <div class="herb-detail">
                <div class="herb-detail-header">
                    <div>
                        <div class="herb-detail-name">${herb.name}</div>
                        ${herb.grade ? `<div class="herb-detail-grade ${getGradeClass(herb.grade)}">${herb.grade}</div>` : ''}
                    </div>
                </div>
                
                <div class="nature-tags">
                    ${herb.nature ? `<span class="nature-tag">${herb.nature}</span>` : ''}
                    ${herb.flavor ? `<span class="nature-tag">${Array.isArray(herb.flavor) ? herb.flavor.join('、') : herb.flavor}</span>` : ''}
                    ${herb.meridian ? `<span class="nature-tag">归${Array.isArray(herb.meridian) ? herb.meridian.join('、') : herb.meridian}经</span>` : ''}
                </div>
                
                ${herb.efficacy ? `
                <div class="detail-section">
                    <h4>功效</h4>
                    <div class="detail-text">${herb.efficacy}</div>
                </div>
                ` : ''}
                
                ${herb.indications ? `
                <div class="detail-section">
                    <h4>主治</h4>
                    <div class="detail-text">${herb.indications}</div>
                </div>
                ` : ''}
                
                ${herb.classic_text ? `
                <div class="detail-section">
                    <h4>经典原文</h4>
                    <div class="classic-text">${herb.classic_text}</div>
                </div>
                ` : ''}
                
                ${herb.dosage ? `
                <div class="detail-section">
                    <h4>用量</h4>
                    <div class="detail-text">${herb.dosage}</div>
                </div>
                ` : ''}
                
                ${herb.contraindications ? `
                <div class="detail-section">
                    <h4>禁忌</h4>
                    <div class="detail-text" style="color: #e57373;">${herb.contraindications}</div>
                </div>
                ` : ''}
            </div>
        `;
    } catch (error) {
        detail.innerHTML = `
            <div class="herb-detail">
                <div class="detail-section">
                    <div class="detail-text" style="color: var(--text-secondary); text-align: center; padding: 24px;">
                        加载失败，请稍后重试
                    </div>
                </div>
            </div>
        `;
        console.error(error);
    }
}

// ============================================
// 辨证相关
// ============================================

function addSymptom() {
    const input = document.getElementById('symptom-input');
    const symptom = input.value.trim();
    
    if (symptom && !state.symptoms.includes(symptom)) {
        state.symptoms.push(symptom);
        renderSymptomTags();
    }
    
    input.value = '';
    input.focus();
}

function addQuickSymptom(symptom) {
    if (!state.symptoms.includes(symptom)) {
        state.symptoms.push(symptom);
        renderSymptomTags();
    }
}

function removeSymptom(symptom) {
    state.symptoms = state.symptoms.filter(s => s !== symptom);
    renderSymptomTags();
}

function renderSymptomTags() {
    const container = document.getElementById('symptom-tags');
    container.innerHTML = state.symptoms.map(symptom => `
        <div class="symptom-tag">
            ${symptom}
            <span class="remove" onclick="removeSymptom('${symptom}')">&times;</span>
        </div>
    `).join('');
}

async function diagnose() {
    if (state.symptoms.length === 0) {
        showToast('请先添加症状');
        return;
    }
    
    const btn = document.getElementById('diagnose-btn');
    const resultDiv = document.getElementById('diagnosis-result');
    const content = document.getElementById('result-content');
    
    btn.disabled = true;
    btn.textContent = '分析中...';
    
    try {
        const response = await fetch(`${API_BASE}/diagnosis/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symptoms: state.symptoms,
                top_k: 5,
                min_score: 0.1
            })
        });
        
        const data = await response.json();
        
        resultDiv.style.display = 'block';
        content.innerHTML = `
            <div class="result-section">
                <h4>识别证型</h4>
                ${data.matched_syndromes.map(s => `
                    <div class="syndrome-match">
                        <div class="syndrome-name">
                            ${s.syndrome_name}
                            <span class="syndrome-score">${Math.round(s.score * 100)}%</span>
                        </div>
                        <div class="syndrome-desc">${s.description}</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="result-section">
                <h4>推荐方剂</h4>
                ${data.recommended_formulas.map(f => `
                    <div class="recommended-formula" onclick="showFormulaDetail('${f.id}')">
                        <div class="formula-header">
                            <span class="name">${f.name}</span>
                            <span class="match-score">匹配度 ${Math.round(f.match_score * 100)}%</span>
                        </div>
                        <div class="formula-indications">${f.indications}</div>
                        <div class="formula-source">${f.source}</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="disclaimer">
                ${data.disclaimer}
            </div>
        `;
        
        // 滚动到结果
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        showToast('辨证分析失败');
        console.error(error);
    } finally {
        btn.disabled = false;
        btn.textContent = '开始辨证';
    }
}

// ============================================
// 首页搜索
// ============================================

function handleHomeSearch() {
    const keyword = document.getElementById('home-search').value.trim();
    if (!keyword) return;
    
    // 切换到方剂页面并搜索
    showPage('formulas');
    document.getElementById('formula-search').value = keyword;
    searchFormulas();
}

// ============================================
// 工具函数
// ============================================

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ============================================
// 事件绑定
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // 回车添加症状（智能辨证功能开发中，元素可能不存在）
    const symptomInput = document.getElementById('symptom-input');
    if (symptomInput) {
        symptomInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addSymptom();
            }
        });
    }
    
    // 回车搜索方剂
    const formulaSearch = document.getElementById('formula-search');
    if (formulaSearch) {
        formulaSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchFormulas();
            }
        });
    }
    
    // 回车搜索药材
    const herbSearch = document.getElementById('herb-search');
    if (herbSearch) {
        herbSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchHerbs();
            }
        });
    }
    
    // 回车首页搜索
    const homeSearch = document.getElementById('home-search');
    if (homeSearch) {
        homeSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleHomeSearch();
            }
        });
    }
    
    // 点击弹窗外部关闭
    document.getElementById('formula-modal').addEventListener('click', (e) => {
        if (e.target.id === 'formula-modal') {
            closeModal();
        }
    });
    
    document.getElementById('herb-modal').addEventListener('click', (e) => {
        if (e.target.id === 'herb-modal') {
            closeHerbModal();
        }
    });
    
    // ESC 关闭弹窗
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeHerbModal();
        }
    });
});
