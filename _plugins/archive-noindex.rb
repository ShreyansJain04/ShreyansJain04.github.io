# Keep thin tag/year/category archive pages out of sitemap.xml.
# They also get <meta name="robots" content="noindex, follow"> in metadata.html.
Jekyll::Hooks.register :site, :pre_render do |site|
  site.pages.each do |page|
    next unless defined?(Jekyll::Archives::Archive) && page.is_a?(Jekyll::Archives::Archive)
    page.data['sitemap'] = false
  end
end
