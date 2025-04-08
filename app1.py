import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  

# Set Streamlit page config
st.set_page_config(page_title="UPSC Data Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("UPSC_CSE_Results.csv")

# Title and Sidebar
st.title("📊 UPSC Civil Services Results Dashboard")
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", [
    "Overview", "Selection Breakdown", "Category-wise Analysis", 
    "Service Allotment", "State Insights", "Score Distributions", "Correlations & Trends"
])

# Cutoff dictionary
cutoff = {
    "General": {"Prelims": 90, "Mains": 750, "Interview": 150, "Final": 950},
    "OBC": {"Prelims": 87, "Mains": 730, "Interview": 140, "Final": 920},
    "SC": {"Prelims": 75, "Mains": 650, "Interview": 130, "Final": 850},
    "ST": {"Prelims": 70, "Mains": 620, "Interview": 120, "Final": 820}
}

# Selection Classification
@st.cache_data
def classify_data(df):
    selected = 0
    prelims_fail = 0
    mains_fail = 0
    interview_fail = 0

    for _, row in df.iterrows():
        category = row["Category"]
        if category in cutoff:
            c = cutoff[category]
            if row["Prelims_Score"] >= c["Prelims"]:
                if row["Mains_Score"] >= c["Mains"]:
                    if row["Interview_Score"] >= c["Interview"]:
                        if row["Final_Score"] >= c["Final"]:
                            selected += 1
                        else:
                            interview_fail += 1
                    else:
                        mains_fail += 1
                else:
                    prelims_fail += 1
    return selected, prelims_fail, mains_fail, interview_fail

selected_count, prelims_fail, mains_fail, interview_fail = classify_data(df)

# Main sections
if page == "Overview":
    st.subheader("📈 Average Scores Over the Years")
    avg_scores = df.groupby('Year')[['Prelims_Score', 'Mains_Score', 'Final_Score']].mean()
    st.line_chart(avg_scores)

    st.subheader("🎯 Distribution of Final Scores")
    fig, ax = plt.subplots()
    sns.histplot(df['Final_Score'], kde=True, bins=30, color='teal', ax=ax)
    st.pyplot(fig)

elif page == "Selection Breakdown":
    st.subheader("✅ Selection vs Not Selected")
    pie_labels = ["Selected", "Not Selected"]
    pie_values = [selected_count, prelims_fail + mains_fail + interview_fail]
    fig, ax = plt.subplots()
    ax.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', colors=["blue", "red"])
    ax.set_title("UPSC Selection Breakdown")
    st.pyplot(fig)

    st.subheader("📉 Where Candidates Failed")
    fail_labels = ["Prelims ➡ Mains", "Mains ➡ Interview", "Interview ➡ Final"]
    fail_values = [prelims_fail, mains_fail, interview_fail]
    fig2, ax2 = plt.subplots()
    ax2.pie(fail_values, labels=fail_labels, autopct='%1.1f%%', colors=["orange", "yellow", "purple"])
    ax2.set_title("Stages Where Candidates Dropped")
    st.pyplot(fig2)

elif page == "Category-wise Analysis":
    st.subheader("🎓 Final Score Distribution by Category")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.violinplot(x='Category', y='Final_Score', data=df, ax=ax)
    st.pyplot(fig)

    st.subheader("🏆 Success Rate by Category")
    cat_success = df.groupby('Category')['Selection_Status'].value_counts(normalize=True).unstack()
    st.bar_chart(cat_success)

elif page == "Service Allotment":
    st.subheader("📌 Number of Candidates by Service Allotment")
    service_counts = df['Service_Allotted'].value_counts()
    fig, ax = plt.subplots()
    service_counts.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_ylabel("Count")
    ax.set_xlabel("Service")
    ax.set_title("Service Allotment")
    st.pyplot(fig)

elif page == "State Insights":
    st.subheader("🗺 Selected Candidates by State")
    state_selection = df[df['Selection_Status'] == 'Yes'].groupby('State').size().reset_index(name='Count')
    fig = px.choropleth(
        state_selection, locations='State', locationmode='geojson-id',
        color='Count', title="Selected Candidates by State"
    )
    st.plotly_chart(fig)

    st.subheader("📦 Final Score by Top 10 States")
    top_states = df['State'].value_counts().nlargest(10).index
    df_top = df[df['State'].isin(top_states)]
    fig2, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='State', y='Final_Score', data=df_top, ax=ax)
    st.pyplot(fig2)

elif page == "Score Distributions":
    st.subheader("📍 Final Score vs AIR Rank (by Category)")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(x='Final_Score', y='AIR (All India Rank)', hue='Category', alpha=0.7, data=df, ax=ax)
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("🔝 Top 20 Ranks - Lollipop Chart")
    top_20 = df.nsmallest(20, 'AIR (All India Rank)').sort_values('AIR (All India Rank)')
    fig2, ax2 = plt.subplots()
    ax2.stem(top_20['AIR (All India Rank)'], top_20['Final_Score'], basefmt=" ")
    ax2.set_title("Final Score of Top 20 Ranks")
    ax2.invert_xaxis()
    st.pyplot(fig2)

elif page == "Correlations & Trends":
    st.subheader("📊 Correlation Between Scores")
    corr = df[['Prelims_Score', 'Mains_Score', 'Interview_Score', 'Final_Score']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    st.subheader("📈 Interview Score Trends Over Years")
    interview_trend = df.groupby('Year')['Interview_Score'].mean()
    st.line_chart(interview_trend)

    st.subheader("🔁 Pairplot of All Scores")
    st.info("Note: Pairplot may take time depending on dataset size.")
    sns_plot = sns.pairplot(df[['Prelims_Score', 'Mains_Score', 'Interview_Score', 'Final_Score']], diag_kind='kde')
    st.pyplot(sns_plot.fig)

# Footer
st.markdown("---")
st.markdown("Made with ❤ using Streamlit | Data Source: UPSC Results Dataset")